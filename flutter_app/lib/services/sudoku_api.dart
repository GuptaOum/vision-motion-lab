import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;

import '../models/solve_result.dart';

class SudokuApiException implements Exception {
  final String message;
  SudokuApiException(this.message);

  @override
  String toString() => message;
}

class SudokuApi {
  // Where the FastAPI backend is running:
  //   Android emulator .... http://10.0.2.2:8000
  //   iOS simulator ....... http://localhost:8000
  //   Real device / web ... http://<your-computer-LAN-IP>:8000
  final String baseUrl;

  SudokuApi({this.baseUrl = 'http://10.0.2.2:8000'});

  Future<SolveResult> solve(
    Uint8List imageBytes, {
    String filename = 'puzzle.jpg',
    bool includeImage = true,
  }) async {
    final uri = Uri.parse('$baseUrl/solve')
        .replace(queryParameters: {'include_image': '$includeImage'});

    final request = http.MultipartRequest('POST', uri)
      ..files.add(http.MultipartFile.fromBytes('file', imageBytes, filename: filename));

    http.StreamedResponse streamed;
    try {
      streamed = await request.send();
    } catch (_) {
      throw SudokuApiException(
        'Could not reach the server at $baseUrl. '
        'Is the backend running and the URL correct?',
      );
    }

    final response = await http.Response.fromStream(streamed);
    if (response.statusCode == 200) {
      return SolveResult.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    }

    String detail;
    try {
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      detail = body['detail']?.toString() ?? response.body;
    } catch (_) {
      detail = response.body;
    }
    throw SudokuApiException(detail);
  }
}
