import 'package:flutter/material.dart';

class SudokuGrid extends StatelessWidget {
  final List<List<int>> detected;
  final List<List<int>> solved;

  const SudokuGrid({super.key, required this.detected, required this.solved});

  @override
  Widget build(BuildContext context) {
    const thin = 0.5;
    const thick = 2.0;
    final line = Theme.of(context).colorScheme.onSurface;

    return AspectRatio(
      aspectRatio: 1,
      child: Container(
        decoration: BoxDecoration(border: Border.all(color: line, width: thick)),
        child: Column(
          children: List.generate(9, (r) {
            return Expanded(
              child: Row(
                children: List.generate(9, (c) {
                  final value = solved[r][c];
                  final isClue = detected[r][c] != 0;
                  return Expanded(
                    child: Container(
                      decoration: BoxDecoration(
                        border: Border(
                          top: BorderSide(width: r % 3 == 0 ? thick : thin, color: line),
                          left: BorderSide(width: c % 3 == 0 ? thick : thin, color: line),
                        ),
                      ),
                      alignment: Alignment.center,
                      child: FittedBox(
                        child: Padding(
                          padding: const EdgeInsets.all(6),
                          child: Text(
                            value == 0 ? '' : '$value',
                            style: TextStyle(
                              fontWeight: isClue ? FontWeight.bold : FontWeight.w400,
                              color: isClue
                                  ? line
                                  : Theme.of(context).colorScheme.primary,
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
