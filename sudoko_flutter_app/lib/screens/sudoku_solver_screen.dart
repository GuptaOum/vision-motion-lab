import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../services/session.dart';
import '../services/sudoku_api.dart';
import '../widgets/editable_sudoku_grid.dart';
import '../widgets/sudoku_grid.dart';
import 'history_screen.dart';
import 'login_screen.dart';

class SudokuSolverScreen extends StatefulWidget {
  const SudokuSolverScreen({super.key});

  @override
  State<SudokuSolverScreen> createState() => _SudokuSolverScreenState();
}

class _SudokuSolverScreenState extends State<SudokuSolverScreen> {
  final _api = SudokuApi();
  final _picker = ImagePicker();

  String? _username;
  Uint8List? _imageBytes;
  List<List<int>>? _grid; // editable, detected then user-corrected
  List<List<int>>? _solved;
  ({int r, int c})? _selected;
  Set<String> _conflicts = {};
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadSession();
  }

  Future<void> _loadSession() async {
    _api.authToken = await Session.token();
    final name = await Session.username();
    if (mounted) setState(() => _username = name);
  }

  Future<void> _logout() async {
    await Session.clear();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  void _handleUnauthorized() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Session expired - please log in again.')),
    );
    _logout();
  }

  Future<void> _pick(ImageSource source) async {
    final picked = await _picker.pickImage(source: source, maxWidth: 1600);
    if (picked == null) return;
    final bytes = await picked.readAsBytes();
    setState(() {
      _imageBytes = bytes;
      _grid = null;
      _solved = null;
      _selected = null;
      _conflicts = {};
      _error = null;
    });
    await _read();
  }

  Future<void> _read() async {
    final bytes = _imageBytes;
    if (bytes == null) return;
    setState(() {
      _loading = true;
      _error = null;
      _solved = null;
    });
    try {
      final grid = await _api.read(bytes);
      setState(() {
        _grid = grid;
        _selected = null;
        _conflicts = {};
      });
    } on SudokuApiException catch (e) {
      setState(() => _error = e.message);
    } catch (e) {
      setState(() => _error = 'Something went wrong: $e');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _setDigit(int n) {
    final sel = _selected;
    final g = _grid;
    if (sel == null || g == null) return;
    setState(() {
      g[sel.r][sel.c] = n;
      _conflicts = {};
    });
  }

  Future<void> _solve() async {
    final g = _grid;
    if (g == null) return;
    setState(() {
      _loading = true;
      _error = null;
      _conflicts = {};
    });
    try {
      final solved = await _api.solve(g);
      setState(() {
        _solved = solved;
        _selected = null;
      });
      if (mounted && _api.authToken != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
              content: Text('Solved - saved to your history'),
              duration: Duration(seconds: 2)),
        );
      }
    } on SudokuApiException catch (e) {
      if (e.unauthorized) {
        _handleUnauthorized();
        return;
      }
      setState(() {
        _error = e.message;
        _conflicts = e.conflicts.map((p) => '${p[0]},${p[1]}').toSet();
      });
    } catch (e) {
      setState(() => _error = 'Something went wrong: $e');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _newPhoto() {
    setState(() {
      _imageBytes = null;
      _grid = null;
      _solved = null;
      _selected = null;
      _conflicts = {};
      _error = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Text(_username == null ? 'Sudoku Solver' : 'Hi, $_username'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            tooltip: 'My solves',
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => HistoryScreen(api: _api)),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Log out',
            onPressed: _logout,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (_imageBytes == null && _grid == null) ...[
              const SizedBox(height: 24),
              Icon(Icons.document_scanner_outlined,
                  size: 72, color: theme.colorScheme.primary),
              const SizedBox(height: 8),
              Text(
                'Scan a Sudoku puzzle',
                textAlign: TextAlign.center,
                style: theme.textTheme.titleLarge,
              ),
              Text(
                'Printed or handwritten - take a photo or pick one.',
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyMedium
                    ?.copyWith(color: theme.colorScheme.outline),
              ),
              const SizedBox(height: 24),
            ],
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _loading ? null : () => _pick(ImageSource.gallery),
                    icon: const Icon(Icons.photo_library_outlined),
                    label: const Text('Gallery'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _loading ? null : () => _pick(ImageSource.camera),
                    icon: const Icon(Icons.photo_camera_outlined),
                    label: const Text('Camera'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            if (_loading)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 8),
                child: LinearProgressIndicator(),
              ),

            if (_error != null) ...[
              Card(
                color: theme.colorScheme.errorContainer,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Text(
                    _error!,
                    style: TextStyle(color: theme.colorScheme.onErrorContainer),
                  ),
                ),
              ),
              const SizedBox(height: 12),
            ],

            // --- REVIEW / EDIT phase ---
            if (_grid != null && _solved == null) ...[
              Text('Check the numbers', style: theme.textTheme.titleMedium),
              const SizedBox(height: 4),
              Text(
                'Tap a cell and fix anything the scanner got wrong, then tap Solve.',
                style: theme.textTheme.bodySmall,
              ),
              const SizedBox(height: 8),
              EditableSudokuGrid(
                grid: _grid!,
                selected: _selected,
                conflicts: _conflicts,
                onTap: (r, c) => setState(() => _selected = (r: r, c: c)),
              ),
              const SizedBox(height: 12),
              _NumberPad(
                enabled: _selected != null && !_loading,
                onDigit: _setDigit,
              ),
              const SizedBox(height: 12),
              FilledButton.icon(
                onPressed: _loading ? null : _solve,
                icon: const Icon(Icons.auto_awesome),
                label: const Text('Solve'),
              ),
              TextButton(
                onPressed: _loading ? null : _newPhoto,
                child: const Text('New photo'),
              ),
            ],

            // --- SOLVED phase ---
            if (_solved != null) ...[
              Text('Solved', style: theme.textTheme.titleMedium),
              const SizedBox(height: 8),
              SudokuGrid(detected: _grid!, solved: _solved!),
              const SizedBox(height: 8),
              Text(
                'Bold = your numbers   ·   colored = filled in by the solver',
                style: theme.textTheme.bodySmall,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => setState(() => _solved = null),
                      child: const Text('Edit'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: FilledButton(
                      onPressed: _newPhoto,
                      child: const Text('New photo'),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _NumberPad extends StatelessWidget {
  final bool enabled;
  final void Function(int) onDigit;

  const _NumberPad({required this.enabled, required this.onDigit});

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      alignment: WrapAlignment.center,
      children: [
        for (var n = 1; n <= 9; n++)
          SizedBox(
            width: 56,
            height: 48,
            child: OutlinedButton(
              onPressed: enabled ? () => onDigit(n) : null,
              style: OutlinedButton.styleFrom(padding: EdgeInsets.zero),
              child: Text('$n', style: const TextStyle(fontSize: 18)),
            ),
          ),
        SizedBox(
          width: 56,
          height: 48,
          child: OutlinedButton(
            onPressed: enabled ? () => onDigit(0) : null,
            style: OutlinedButton.styleFrom(padding: EdgeInsets.zero),
            child: const Icon(Icons.backspace_outlined, size: 18),
          ),
        ),
      ],
    );
  }
}
