import 'package:shared_preferences/shared_preferences.dart';

/// Persists the logged-in user's token + name across app restarts.
class Session {
  static const _kToken = 'auth_token';
  static const _kUsername = 'username';

  static Future<void> save(String token, String username) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_kToken, token);
    await prefs.setString(_kUsername, username);
  }

  static Future<String?> token() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_kToken);
  }

  static Future<String?> username() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_kUsername);
  }

  static Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_kToken);
    await prefs.remove(_kUsername);
  }
}
