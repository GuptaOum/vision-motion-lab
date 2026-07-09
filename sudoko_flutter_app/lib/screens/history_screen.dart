import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../services/sudoku_api.dart';
import '../widgets/sudoku_grid.dart';

class HistoryScreen extends StatefulWidget {
  final SudokuApi api;

  const HistoryScreen({super.key, required this.api});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<HistoryEntry>? _entries;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _entries = null;
      _error = null;
    });
    try {
      final entries = await widget.api.history();
      if (mounted) setState(() => _entries = entries);
    } on SudokuApiException catch (e) {
      if (mounted) setState(() => _error = e.message);
    } catch (e) {
      if (mounted) setState(() => _error = 'Something went wrong: $e');
    }
  }

  Future<void> _delete(HistoryEntry entry) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete this solve?'),
        content: const Text('This removes it from your history permanently.'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Cancel')),
          FilledButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('Delete')),
        ],
      ),
    );
    if (confirmed != true) return;
    try {
      await widget.api.deleteSolve(entry.id);
      setState(() => _entries?.removeWhere((e) => e.id == entry.id));
    } on SudokuApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.message)));
      }
    }
  }

  void _view(HistoryEntry entry) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (ctx) => Padding(
        padding: const EdgeInsets.fromLTRB(24, 0, 24, 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              DateFormat('d MMM yyyy, h:mm a').format(entry.createdAt),
              textAlign: TextAlign.center,
              style: Theme.of(ctx).textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            SudokuGrid(detected: entry.puzzle, solved: entry.solution),
            const SizedBox(height: 8),
            Text(
              'Bold = your puzzle   ·   colored = solved by the app',
              textAlign: TextAlign.center,
              style: Theme.of(ctx).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('My solves')),
      body: RefreshIndicator(
        onRefresh: _load,
        child: _error != null
            ? ListView(
                padding: const EdgeInsets.all(24),
                children: [
                  Card(
                    color: theme.colorScheme.errorContainer,
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Text(_error!,
                          style: TextStyle(
                              color: theme.colorScheme.onErrorContainer)),
                    ),
                  ),
                  const SizedBox(height: 12),
                  OutlinedButton(
                      onPressed: _load, child: const Text('Try again')),
                ],
              )
            : _entries == null
                ? const Center(child: CircularProgressIndicator())
                : _entries!.isEmpty
                    ? ListView(
                        padding: const EdgeInsets.all(48),
                        children: [
                          Icon(Icons.history,
                              size: 64, color: theme.colorScheme.outline),
                          const SizedBox(height: 12),
                          Text(
                            'No solves yet.\nScan a puzzle and it will show up here.',
                            textAlign: TextAlign.center,
                            style: theme.textTheme.bodyLarge
                                ?.copyWith(color: theme.colorScheme.outline),
                          ),
                        ],
                      )
                    : ListView.separated(
                        padding: const EdgeInsets.all(12),
                        itemCount: _entries!.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 4),
                        itemBuilder: (ctx, i) {
                          final entry = _entries![i];
                          final clues = entry.puzzle
                              .expand((r) => r)
                              .where((v) => v != 0)
                              .length;
                          return Card(
                            child: ListTile(
                              leading: CircleAvatar(
                                backgroundColor:
                                    theme.colorScheme.primaryContainer,
                                child: Icon(Icons.grid_on,
                                    color: theme
                                        .colorScheme.onPrimaryContainer),
                              ),
                              title: Text(DateFormat('d MMM yyyy, h:mm a')
                                  .format(entry.createdAt)),
                              subtitle: Text('$clues clues'),
                              trailing: IconButton(
                                icon: const Icon(Icons.delete_outline),
                                onPressed: () => _delete(entry),
                              ),
                              onTap: () => _view(entry),
                            ),
                          );
                        },
                      ),
      ),
    );
  }
}
