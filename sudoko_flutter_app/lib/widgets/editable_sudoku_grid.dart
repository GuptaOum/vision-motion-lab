import 'package:flutter/material.dart';

class EditableSudokuGrid extends StatelessWidget {
  final List<List<int>> grid;
  final ({int r, int c})? selected;
  final Set<String> conflicts; // "r,c" cells to flag red
  final void Function(int r, int c) onTap;

  const EditableSudokuGrid({
    super.key,
    required this.grid,
    required this.selected,
    required this.onTap,
    this.conflicts = const {},
  });

  @override
  Widget build(BuildContext context) {
    const thin = 0.5;
    const thick = 2.0;
    final theme = Theme.of(context);
    final line = theme.colorScheme.onSurface;

    return AspectRatio(
      aspectRatio: 1,
      child: Container(
        decoration: BoxDecoration(border: Border.all(color: line, width: thick)),
        child: Column(
          children: List.generate(9, (r) {
            return Expanded(
              child: Row(
                children: List.generate(9, (c) {
                  final isSel =
                      selected != null && selected!.r == r && selected!.c == c;
                  final isConf = conflicts.contains('$r,$c');
                  final v = grid[r][c];

                  Color? bg;
                  if (isSel) {
                    bg = theme.colorScheme.primary.withValues(alpha: 0.25);
                  } else if (isConf) {
                    bg = theme.colorScheme.error.withValues(alpha: 0.20);
                  }

                  return Expanded(
                    child: GestureDetector(
                      onTap: () => onTap(r, c),
                      child: Container(
                        decoration: BoxDecoration(
                          color: bg,
                          border: Border(
                            top: BorderSide(
                                width: r % 3 == 0 ? thick : thin, color: line),
                            left: BorderSide(
                                width: c % 3 == 0 ? thick : thin, color: line),
                          ),
                        ),
                        alignment: Alignment.center,
                        child: FittedBox(
                          child: Padding(
                            padding: const EdgeInsets.all(6),
                            child: Text(
                              v == 0 ? '' : '$v',
                              style: TextStyle(
                                fontWeight: FontWeight.w600,
                                color: isConf ? theme.colorScheme.error : line,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  );
                }),
              ),
            );
          }),
        ),
      ),
    );
  }
}
