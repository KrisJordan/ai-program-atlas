// Offline PDFKit text extraction; source retrieval must separately honor robots.
// Usage: swift -module-cache-path /tmp/atlas-swift-module-cache extract_pdf.swift public.pdf > public.txt
import Foundation
import PDFKit
if CommandLine.arguments.count != 2 {
    fatalError("Supply one local PDF path")
}
guard let document = PDFDocument(url: URL(fileURLWithPath: CommandLine.arguments[1])) else {
    fatalError("Cannot read local PDF")
}
for index in 0..<document.pageCount {
    print(document.page(at: index)?.string ?? "")
}
