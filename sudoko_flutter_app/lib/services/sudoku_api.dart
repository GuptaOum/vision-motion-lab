import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;

class SudokuApiException implements Exception {
  final String message;
  final List<List<int>> conflicts; // [[row, col], ...] cells to highlight

  SudokuApiException(this.message, {this.conflicts = const []});

  @override
  String toString() => message;
}

class SudokuApi {
  // Deployed FastAPI backend (EC2, ap-south-1). For local dev, pass a baseUrl:
  //   Android emulator .... http://10.0.2.2:8000
  //   iOS simulator ....... http://localhost:8000
  //   Real device / web ... http://<your-computer-LAN-IP>:8000
  final String baseUrl;

  SudokuApi({this.baseUrl = 'http://3.109.177.77:8000'});

  static const _unreachable =
      'Could not reach the server. Is it running and are you online?';

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
    throw _errorFrom(response.body);
  }

  /// Solve a user-confirmed 9x9 grid. On a rule conflict the exception carries
  /// the offending cells so the UI can highlight them.
  Future<List<List<int>>> solve(List<List<int>> grid) async {
    http.Response response;
    try {
      response = await http.post(
        Uri.parse('$baseUrl/solve'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'grid': grid}),
      );
    } catch (_) {
      throw SudokuApiException(_unreachable);
    }
    if (response.statusCode == 200) {
      return _parseGrid((jsonDecode(response.body) as Map)['solved']);
    }
    throw _errorFrom(response.body);
  }

  SudokuApiException _errorFrom(String body) {
    dynamic detail;
    try {
      detail = (jsonDecode(body) as Map)['detail'];
    } catch (_) {
      return SudokuApiException(body.isEmpty ? 'Request failed.' : body);
    }
    if (detail is Map) {
      final conflicts = (detail['conflicts'] as List?)
              ?.map((p) => (p as List).map((n) => (n as num).toInt()).toList())
              .toList() ??
          const <List<int>>[];
      return SudokuApiException(
          detail['message']?.toString() ?? 'Request failed.',
          conflicts: conflicts);
    }
    return SudokuApiException(detail?.toString() ?? 'Request failed.');
  }
}
