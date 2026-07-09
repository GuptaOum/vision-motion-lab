import 'package:flutter/material.dart';

import 'screens/sudoku_solver_screen.dart';

void main() => runApp(const SudokuSolverApp());

class SudokuSolverApp extends StatelessWidget {
  const SudokuSolverApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Sudoku Solver',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
      home: const SudokuSolverScreen(),
    );
  }
}
