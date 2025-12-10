from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document

class AstrologyPDFLoaderService:
    # Service for loading PDF documents from the knowledge base. 
    # Extracts text content and metadata from astrology PDF files.
    def __init__(self, pdf_directory: str = "./rag_sources"):
        # Initialize PDF loader service.
        self.pdf_directory = Path(pdf_directory)
        if not self.pdf_directory.exists():
            raise ValueError(f"PDF directory does not exist: {pdf_directory}")

        logger.info(f"Initialized PDFLoaderService with directory: {self.pdf_directory}")

    def get_pdf_files(self) -> List[Path]:
        # Get all PDF files in the configured directory.
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in {self.pdf_directory}")
        return pdf_files

    def load_single_pdf(
        self,
        pdf_path: Path,
        extract_images: bool = False
    ) -> List[Document]:
        # Load a single PDF file and extract its content
        try:
            logger.info(f"Loading PDF: {pdf_path.name}")

            # Use LangChain's PyPDFLoader
            loader = PyPDFLoader(str(pdf_path))
            documents = loader.load()

            # Enrich metadata
            for i, doc in enumerate(documents):
                doc.metadata.update({
                    "source_file": pdf_path.name,
                    "source_path": str(pdf_path),
                    "page_number": i + 1,
                    "total_pages": len(documents),
                    "file_type": "pdf",
                    "category": self._categorize_document(pdf_path.name)
                })

            logger.info(
                f"Successfully loaded {len(documents)} pages from {pdf_path.name}"
            )
            return documents

        except Exception as e:
            logger.error(f"Error loading PDF {pdf_path.name}: {str(e)}")
            raise

    def load_all_pdfs(
        self,
        extract_images: bool = False
    ) -> Dict[str, List[Document]]:
        # Load all PDF files from the configured directory.
        all_documents = {}
        pdf_files = self.get_pdf_files()

        if not pdf_files:
            logger.warning("No PDF files found to load")
            return all_documents

        logger.info(f"Loading {len(pdf_files)} PDF files...")

        for pdf_path in pdf_files:
            try:
                documents = self.load_single_pdf(
                    pdf_path,
                    extract_images=extract_images
                )
                all_documents[pdf_path.name] = documents

            except Exception as e:
                logger.error(f"Failed to load {pdf_path.name}: {str(e)}")
                continue

        total_pages = sum(len(docs) for docs in all_documents.values())
        logger.info(
            f"Successfully loaded {len(all_documents)} PDFs "
            f"with {total_pages} total pages"
        )

        return all_documents

    def load_all_pdfs_flat(
        self,
        extract_images: bool = False
    ) -> List[Document]:
        # Load all PDFs and return a flat list of all documents.
        all_docs_dict = self.load_all_pdfs(extract_images=extract_images)

        # Flatten the dictionary into a single list
        flat_documents = []
        for pdf_name, documents in all_docs_dict.items():
            flat_documents.extend(documents)

        logger.info(f"Flattened {len(flat_documents)} total documents")
        return flat_documents

    def _categorize_document(self, filename: str) -> str:
        # Categorize document based on filename.
        filename_lower = filename.lower()

        # Categorize based on keywords in filename
        if "aspect" in filename_lower:
            return "aspects"
        elif "house" in filename_lower:
            return "houses"
        elif "element" in filename_lower:
            return "elements"
        elif "hellenistic" in filename_lower:
            return "hellenistic_astrology"
        elif "psychology" in filename_lower:
            return "psychological_astrology"
        elif "interpretation" in filename_lower or "chart" in filename_lower:
            return "chart_interpretation"
        else:
            return "general_astrology"

    def get_document_stats(self) -> Dict[str, any]:
        # Get statistics about loaded documents.
        all_docs = self.load_all_pdfs_flat()

        # Calculate statistics
        total_chars = sum(len(doc.page_content) for doc in all_docs)
        avg_chars_per_page = total_chars / len(all_docs) if all_docs else 0

        # Count by category
        categories = {}
        for doc in all_docs:
            category = doc.metadata.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1

        stats = {
            "total_documents": len(all_docs),
            "total_characters": total_chars,
            "average_chars_per_page": round(avg_chars_per_page, 2),
            "documents_by_category": categories,
            "pdf_files": len(self.get_pdf_files())
        }

        logger.info(f"Document statistics: {stats}")
        return stats

# Factory function to get a PDFLoaderService instance
def get_astrology_pdf_loader(pdf_directory: str = "./rag_sources") -> AstrologyPDFLoaderService:
    return AstrologyPDFLoaderService(pdf_directory=pdf_directory)
