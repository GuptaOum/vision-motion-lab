import 'dart:convert';
import 'dart:typed_data';

class SolveResult {
  final List<List<int>> detected;
  final List<List<int>> solved;
  final Uint8List? solvedImage;

  SolveResult({
    required this.detected,
    required this.solved,
    this.solvedImage,
  });

  factory SolveResult.fromJson(Map<String, dynamic> json) {
    List<List<int>> parseGrid(dynamic raw) => (raw as List)
        .map((row) => (row as List).map((n) => (n as num).toInt()).toList())
        .toList();

    Uint8List? image;
    final b64 = json['solved_image_png_base64'];
    if (b64 is String && b64.isNotEmpty) {
      image = base64Decode(b64);
    }

    return SolveResult(
      detected: parseGrid(json['detected']),
      solved: parseGrid(json['solved']),
      solvedImage: image,
    );
  }
}
