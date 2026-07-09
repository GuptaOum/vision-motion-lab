import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;

// Deployed FastAPI backend (EC2, ap-south-1). For local dev:
//   Android emulator .... http://10.0.2.2:8000
//   iOS simulator ....... http://localhost:8000
//   Real device / web ... http://<your-computer-LAN-IP>:8000
const kServerBaseUrl = 'http://3.109.177.77:8000';

class SudokuApiException implements Exception {
  final String message;
  final List<List<int>> conflicts; // [[row, col], ...] cells to highlight
  final bool unauthorized;

  SudokuApiException(this.message,
      {this.conflicts = const [], this.unauthorized = false});

  @override
  String toString() => message;
}

class HistoryEntry {
  final int id;
  final DateTime createdAt;
  final List<List<int>> puzzle;
  final List<List<int>> solution;

  HistoryEntry({
    required this.id,
    required this.createdAt,
    required this.puzzle,
    required this.solution,
  });
}

class SudokuApi {
  final String baseUrl;

  /// Bearer token of the logged-in user; solves are saved to their history.
  String? authToken;

  SudokuApi({this.baseUrl = kServerBaseUrl, this.authToken});

  static const _unreachable =
      'Could not reach the server. Is it running and are you online?';

  Map<String, String> get _authHeaders =>
      authToken == null ? {} : {'Authorization': 'Bearer $authToken'};

  List<List<int>> _parseGrid(dynamic raw) => (raw as List)
      .map((row) => (row as List).map((n) => (n as num).toInt()).toList())
      .toList();

  /// OCR only: send an image, get back the detected 9x9 grid (0 = blank).
  Future<List<List<int>>> read(Uint8List imageBytes,
      {String filename = 'puzzle.jpg'}) async {
    final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/read'))
      ..files.add(
          http.MultipartFile.fromBytes('file', imageBytes, filename: filename));

    http.StreamedResponse streamed;
    try {
      streamed = await request.send();
    } catch (_) {
      throw SudokuApiException(_unreachable);
    }
    final response = await http.Response.fromStream(streamed);
    if (response.statusCode == 200) {
      return _parseGrid((jsonDecode(response.body) as Map)['detected']);
    }
    throw _errorFrom(response);
  }

  /// Solve a user-confirmed 9x9 grid. Saved to history when logged in.
  Future<List<List<int>>> solve(List<List<int>> grid) async {
    http.Response response;
    try {
      response = await http.post(
        Uri.parse('$baseUrl/solve'),
        headers: {'Content-Type': 'application/json', ..._authHeaders},
        body: jsonEncode({'grid': grid}),
      );
    } catch (_) {
      throw SudokuApiException(_unreachable);
    }
    if (response.statusCode == 200) {
      return _parseGrid((jsonDecode(response.body) as Map)['solved']);
    }
    throw _errorFrom(response);
  }

  /// The logged-in user's past solves, newest first.
  Future<List<HistoryEntry>> history() async {
    http.Response response;
    try {
      response =
          await http.get(Uri.parse('$baseUrl/history'), headers: _authHeaders);
    } catch (_) {
      throw SudokuApiException(_unreachable);
    }
    if (response.statusCode == 200) {
      final solves = (jsonDecode(response.body) as Map)['solves'] as List;
      return solves.map((s) {
        final m = s as Map<String, dynamic>;
        return HistoryEntry(
          id: (m['id'] as num).toInt(),
          createdAt:
              DateTime.tryParse(m['created_at'] as String? ?? '')?.toLocal() ??
                  DateTime.now(),
          puzzle: _parseGrid(m['puzzle']),
          solution: _parseGrid(m['solution']),
        );
      }).toList();
    }
    throw _errorFrom(response);
  }

  Future<void> deleteSolve(int id) async {
    http.Response response;
    try {
      response = await http.delete(Uri.parse('$baseUrl/history/$id'),
          headers: _authHeaders);
    } catch (_) {
      throw SudokuApiException(_unreachable);
    }
    if (response.statusCode != 200) throw _errorFrom(response);
  }

  SudokuApiException _errorFrom(http.Response response) {
    final unauthorized = response.statusCode == 401;
    dynamic detail;
    try {
      detail = (jsonDecode(response.body) as Map)['detail'];
    } catch (_) {
      return SudokuApiException(
          response.body.isEmpty ? 'Request failed.' : response.body,
          unauthorized: unauthorized);
    }
    if (detail is Map) {
      final conflicts = (detail['conflicts'] as List?)
              ?.map((p) => (p as List).map((n) => (n as num).toInt()).toList())
              .toList() ??
          const <List<int>>[];
      return SudokuApiException(
          detail['message']?.toString() ?? 'Request failed.',
          conflicts: conflicts,
          unauthorized: unauthorized);
    }
    return SudokuApiException(detail?.toString() ?? 'Request failed.',
        unauthorized: unauthorized);
  }
}
