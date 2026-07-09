import 'package:flutter/material.dart';

import 'screens/login_screen.dart';
import 'screens/sudoku_solver_screen.dart';
import 'services/session.dart';

void main() => runApp(const SudokuSolverApp());

class SudokuSolverApp extends StatelessWidget {
  const SudokuSolverApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Sudoku Solver',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
      darkTheme: ThemeData(
        colorSchemeSeed: Colors.indigo,
        brightness: Brightness.dark,
        useMaterial3: true,
      ),
      themeMode: ThemeMode.system,
      home: const _StartupGate(),
    );
  }
}

/// Routes to the solver when a session exists, otherwise to login.
class _StartupGate extends StatelessWidget {
  const _StartupGate();

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<String?>(
      future: Session.token(),
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        return snapshot.data == null
            ? const LoginScreen()
            : const SudokuSolverScreen();
      },
    );
  }
}
