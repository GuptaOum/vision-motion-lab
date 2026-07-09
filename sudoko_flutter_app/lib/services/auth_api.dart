import 'dart:convert';

import 'package:http/http.dart' as http;

import 'sudoku_api.dart' show SudokuApiException, kServerBaseUrl;

class AuthApi {
  final String baseUrl;

  AuthApi({this.baseUrl = kServerBaseUrl});

  Future<({String token, String username})> login(
          String username, String password) =>
      _post('/auth/login', username, password);

  Future<({String token, String username})> signup(
          String username, String password) =>
      _post('/auth/signup', username, password);

  Future<({String token, String username})> _post(
      String path, String username, String password) async {
    http.Response response;
    try {
      response = await http.post(
        Uri.parse('$baseUrl$path'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': username, 'password': password}),
      );
    } catch (_) {
      throw SudokuApiException(
          'Could not reach the server. Are you online?');
    }
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode == 200) {
      return (
        token: body['token'] as String,
        username: body['username'] as String
      );
    }
    final detail = body['detail'];
    if (detail is List) {
      // FastAPI validation errors
      final msg = detail
          .map((e) => (e as Map)['msg']?.toString() ?? '')
          .where((m) => m.isNotEmpty)
          .join('\n');
      throw SudokuApiException(msg.isEmpty ? 'Invalid input.' : msg);
    }
    throw SudokuApiException(detail?.toString() ?? 'Request failed.');
  }
}
