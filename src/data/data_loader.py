import wikipediaapi
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from nltk.corpus import stopwords

class WikipediaFetcher:
    def __init__(self, language):
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        self.wikipedia = wikipediaapi.Wikipedia(user_agent='final_project', language=language, extract_format=wikipediaapi.ExtractFormat.WIKI)
        self.stop_words = stopwords.words('indonesian')
        extra_stopwords = [
            'apa', 'siapa', 'kapan', 'dimana', 'mengapa', 'bagaimana', 'berapa',
            'apakah', 'siapakah', 'kapanlah', 'mengapakah', 'bagaimanakah',
            'jelaskan', 'sebutkan', 'itu', 'adalah', 'merupakan', 'yaitu', 'terjadi'
        ]
        self.all_stopwords = self.stop_words + extra_stopwords
    
    def _clean_text(self, text):
        """
        Membersihkan teks dari stopwords dan karakter non-alfanumerik.
        """
        text = text.lower()
        # Menghapus tanda baca
        text = re.sub(r'[^\w\s]', '', text)
        # Menghapus stopwords
        words = [word for word in text.split() if word not in self.all_stopwords]
        return " ".join(words)
    
    def extract_keywords(self, question, top_n=3):
        """
        Mengekstrak kata kunci menggunakan CountVectorizer dan cosine similarity
        pada teks yang sudah dibersihkan.
        """
        # Membersihkan pertanyaan sebelum mengekstrak kandidat kata kunci
        clean_question = self._clean_text(question)

        # Jika setelah dibersihkan tidak ada teks, kembalikan teks bersih itu sendiri
        if not clean_question:
            return []

        try:
            # Memperluas rentang n-gram untuk menangkap frasa seperti "perang dunia"
            count = CountVectorizer(ngram_range=(1, 3)).fit([clean_question])
            candidates = count.get_feature_names_out()

            if not candidates.any():
                return [clean_question] # Fallback jika tidak ada kandidat

            # Menggunakan pertanyaan asli untuk embedding agar konteksnya tidak hilang
            doc_embedding = self.model.encode([question])
            candidate_embeddings = self.model.encode(candidates)
            
            distances = cosine_similarity(doc_embedding, candidate_embeddings)
            # Mengambil kandidat dengan skor tertinggi
            keywords = [candidates[index] for index in distances.argsort()[0][-top_n:]]
            return keywords
        except ValueError:
            # Terjadi jika teks bersih hanya berisi stopwords yang tidak ada di vocabulary
            return [clean_question]

    def fetch_wikipedia_articles(self, question):
        """
        Mencari artikel Wikipedia berdasarkan gabungan kata kunci terbaik.
        """
        keywords = self.extract_keywords(question, top_n=3)
        documents = []

        if not keywords:
            return documents

        # Menggabungkan kata kunci menjadi satu query pencarian yang lebih kuat
        for keyword in reversed(keywords):
            try:
                page = self.wikipedia.page(keyword)
                if page.exists():
                    # Jika halaman ditemukan, langsung gunakan dan hentikan pencarian
                    documents.append({"content": page.text, "meta": {"title": page.title}})
                    # Hentikan loop setelah menemukan satu dokumen yang valid
                    return documents 
            except Exception as e:
                print(f"An error occurred during Wikipedia search for '{keyword}': {e}")
                continue # Lanjutkan ke kata kunci berikutnya jika ada error

        # Jika loop selesai dan tidak ada dokumen ditemukan, kembalikan daftar kosong
        return documents