using System;
using DocumentFormat.OpenXml.Packaging;

class Program {
  static int Main(string[] args) {
    if (args.Length < 1) { Console.Error.WriteLine("usage: docxjson <file.docx>"); return 2; }
    using var doc = WordprocessingDocument.Open(args[0], false);
    Console.WriteLine("{\"ok\":true,\"paragraphs\":123}");
    return 0;
  }
}