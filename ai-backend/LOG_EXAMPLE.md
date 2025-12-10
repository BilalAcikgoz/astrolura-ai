# Log Output Examples

## RAG Pipeline Log Çıktısı Örneği

Backend'i çalıştırdığınızda aşağıdaki gibi detaylı loglar göreceksiniz:

### 1. Embedding İşlemleri
```log
2025-12-10 11:42:21 | INFO     | app.rag.embeddings.service - 🔢 Embedding API Call: model=text-embedding-3-small, texts=12, tokens=1,234, cost=$0.000025
2025-12-10 11:42:21 | INFO     | app.rag.embeddings.service - ✅ Embedding complete: 12 total (8 cached, 4 new)
```

### 2. RAG Retrieval İşlemleri
```log
2025-12-10 11:42:21 | INFO     | app.rag.service_manager - Generated 20 queries from birth chart
2025-12-10 11:42:21 | INFO     | app.rag.service_manager - Limited to 12 queries (from 20)
2025-12-10 11:42:21 | INFO     | app.rag.service_manager - 🔍 Starting RAG retrieval with 12 queries...
2025-12-10 11:42:22 | INFO     | app.rag.service_manager - 📚 RAG Retrieval Complete:
├─ Queries: 12
├─ Total Searched: 60
├─ Relevant Chunks: 15
├─ Unique Sources: 5
└─ Avg Similarity Score: 0.8234
```

### 3. LLM Generation (En Önemli - Maliyet Bilgileri)
```log
2025-12-10 11:42:25 | INFO     | app.rag.generation.service - Generating interpretation in tr for Bilal Acikgoz
2025-12-10 11:42:28 | INFO     | app.rag.generation.service - ✨ LLM Generation Complete ✨
├─ Model: gpt-4o-mini-2024-07-18
├─ Input Tokens: 12,543
├─ Output Tokens: 3,892
├─ Total Tokens: 16,435
├─ Input Cost: $0.001881
├─ Output Cost: $0.002335
└─ Total Cost: $0.004216
```

## Toplam Maliyet Hesaplama

Her request için:
- **Embedding Cost**: ~$0.000025 (cached olursa ücretsiz)
- **LLM Generation Cost**: ~$0.004216 (model ve token sayısına göre değişir)
- **Toplam Request Cost**: ~$0.004241

### Model Fiyatları (per 1M tokens)

| Model | Input | Output |
|-------|-------|--------|
| gpt-4o | $2.50 | $10.00 |
| gpt-4o-mini | $0.150 | $0.600 |
| gpt-3.5-turbo | $0.50 | $1.50 |
| text-embedding-3-small | $0.020 | - |
| text-embedding-3-large | $0.130 | - |

## Cache'in Önemi

Cache sayesinde:
- Aynı query'ler için embedding maliyeti **sıfır**
- Response süresi **3-5x daha hızlı**
- ~3500 cached embedding dosyanız var!

## Log Seviyeleri

`.env` dosyasında log seviyesini değiştirebilirsiniz:

```env
LOG_LEVEL=INFO    # Standart loglar (önerilen)
LOG_LEVEL=DEBUG   # Detaylı debug logları (her query'yi gösterir)
LOG_LEVEL=WARNING # Sadece uyarı ve hatalar
```

## Gerçek Zamanlı Maliyet Takibi

Her interpretation request'inde tam maliyet bilgisini görürsünüz:
- ✅ Input token sayısı ve maliyeti
- ✅ Output token sayısı ve maliyeti
- ✅ Toplam maliyet (USD)
- ✅ Kullanılan model adı
- ✅ Cache kullanım oranı

Bu sayede production'da maliyet optimizasyonu yapabilirsiniz! 💰
