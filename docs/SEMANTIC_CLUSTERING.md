# Semantic Clustering Guide

This document explains the semantic clustering feature that uses AI embedding models to cluster keywords based on their meaning and context.

## Overview

Semantic clustering is an alternative to SERP clustering that groups keywords based on their semantic similarity rather than shared SERP URLs. It uses advanced AI embedding models to understand the meaning and context of keywords.

### 🆚 **Semantic vs SERP Clustering Comparison**

| Feature | Semantic Clustering | SERP Clustering |
|---------|-------------------|-----------------|
| **Cost** | ✅ Free (no API costs) | 💰 API costs ($0.50+ per keyword) |
| **Speed** | ⚡ Fast (local processing) | 🐌 Slow (API calls + polling) |
| **Keyword Limit** | ✅ Unlimited | ⚠️ Limited by API costs |
| **Accuracy** | 🎯 Semantic similarity | 🎯 SERP overlap |
| **Internet Required** | 🔄 Only for model download | ✅ Always required |
| **Hardware** | 💻 Local GPU/CPU | ☁️ None |
| **Best For** | Large lists, semantic grouping | Precise SERP targeting |

---

## When to Use Each Method

### 🧠 **Use Semantic Clustering When:**
- Processing large keyword lists (10,000+ keywords)
- Budget constraints (avoiding API costs)
- Semantic/topical grouping is more important than SERP overlap
- Working with broad keyword research
- Need fast results without waiting for API calls
- Working offline or with limited internet

### 🔗 **Use SERP Clustering When:**
- Precise content targeting based on actual SERP results
- Smaller keyword lists (under 5,000 keywords)
- SERP overlap is critical for your strategy
- Budget allows for API costs
- Need the most accurate content targeting

---

## Available Models

### **Recommended Models**

#### 1. **Balanced Models (Best Starting Point)**
- **gte-large** - 2GB+ VRAM, excellent quality/performance balance
- **bge-large-en-v1.5** - 2GB+ VRAM, strong English performance

#### 2. **High Quality Models**
- **sentence-t5-xl** - 5GB+ VRAM, superior clustering quality
- **Qwen3-Embedding-0.6B** - 4GB+ VRAM, fast and efficient

#### 3. **Top Tier Models (Advanced Users)**
- **Qwen3-Embedding-4B** - 10GB+ VRAM, excellent performance
- **Qwen3-Embedding-8B** - 20GB+ VRAM, best quality

### **Model Selection Guide**

| Your Hardware | Recommended Model | Expected Performance |
|---------------|------------------|---------------------|
| CPU Only | gte-large | Good quality, slower speed |
| 2-4GB GPU | gte-large / bge-large | Good quality, fast speed |
| 5-8GB GPU | sentence-t5-xl | High quality, fast speed |
| 10GB+ GPU | Qwen3-Embedding-4B | Excellent quality, very fast |
| 20GB+ GPU | Qwen3-Embedding-8B | Best quality, very fast |

---

## Installation & Setup

### **1. Install Dependencies**

The semantic clustering feature requires additional packages:

```bash
# Install semantic clustering dependencies
pip install -r requirements-semantic.txt

# Or install manually:
pip install sentence-transformers torch transformers
```

### **2. Hardware Requirements**

#### **Minimum Requirements:**
- **CPU**: Any modern processor
- **RAM**: 4GB+ (8GB+ recommended)
- **Storage**: 2-10GB for model files
- **Internet**: Required for initial model download

#### **Recommended for Best Performance:**
- **GPU**: NVIDIA GPU with 4GB+ VRAM
- **RAM**: 16GB+ for large keyword lists
- **Storage**: SSD for faster model loading

### **3. First-Time Setup**

1. Models are downloaded automatically on first use
2. Models are cached locally (no re-download needed)
3. Larger models provide better quality but need more resources

---

## How to Use

### **1. Basic Workflow**

1. **Navigate** to the "🧠 Semantic Clustering" tab
2. **Input Keywords**: Paste keywords or upload CSV file
3. **Select Model**: Choose based on your hardware
4. **Configure Parameters**: Set similarity threshold and cluster size
5. **Start Clustering**: Click the clustering button
6. **Review Results**: Analyze clusters and download results

### **2. Parameter Configuration**

#### **Similarity Threshold (0.1 - 1.0)**
- **0.95-1.0**: Very tight clusters, high precision
- **0.8-0.95**: Balanced clustering (recommended)
- **0.6-0.8**: Broader clusters, higher recall
- **0.1-0.6**: Very broad clusters, may be too loose

#### **Minimum Cluster Size**
- **2**: Include all possible clusters
- **3-5**: Filter out very small clusters
- **5+**: Only larger, more significant clusters

### **3. Interpreting Results**

The results show:
- **Parent Keyword**: The representative keyword for each cluster
- **Child Keyword**: All keywords in the cluster (including parent)
- **Cluster Size**: Number of keywords in each cluster

---

## Performance Optimization

### **Speed Optimization**

1. **Use GPU**: 5-10x faster than CPU
2. **Choose Appropriate Model**: Balance quality vs speed
3. **Batch Processing**: Process very large lists in chunks
4. **Close Other Apps**: Free up GPU/RAM resources

### **Quality Optimization**

1. **Use Larger Models**: Better semantic understanding
2. **Tune Similarity Threshold**: Find the sweet spot for your data
3. **Pre-filter Keywords**: Remove irrelevant keywords first
4. **Domain-Specific Models**: Consider fine-tuned models for your niche

### **Memory Optimization**

1. **Monitor GPU Memory**: Use nvidia-smi to check usage
2. **Reduce Batch Size**: If running out of memory
3. **Use CPU Fallback**: If GPU memory is insufficient
4. **Close Other GPU Applications**: Free up VRAM

---

## Troubleshooting

### **Common Issues**

#### **1. Dependencies Not Installed**
```
Error: Required dependencies not installed
```
**Solution**: Install semantic clustering dependencies
```bash
pip install -r requirements-semantic.txt
```

#### **2. Out of Memory Errors**
```
CUDA out of memory / RuntimeError: out of memory
```
**Solutions**:
- Use a smaller model (gte-large instead of Qwen models)
- Reduce keyword count
- Close other applications
- Use CPU instead of GPU

#### **3. Model Download Failures**
```
Error loading model: Connection timeout
```
**Solutions**:
- Check internet connection
- Try again (downloads can be large)
- Use a different model
- Download manually from HuggingFace

#### **4. No Clusters Formed**
```
No clusters were formed with current settings
```
**Solutions**:
- Lower similarity threshold (try 0.8 or 0.7)
- Reduce minimum cluster size to 2
- Check if keywords are semantically related
- Try a different model

### **Performance Issues**

#### **Slow Processing**
- Use GPU if available
- Try faster models (Qwen-0.6B)
- Process in smaller batches
- Check system resources

#### **Poor Clustering Quality**
- Use larger, higher-quality models
- Adjust similarity threshold
- Pre-process keywords (remove duplicates, irrelevant terms)
- Consider domain-specific models

---

## Advanced Usage

### **Custom Models**

You can use any SentenceTransformer-compatible model:

1. Find models on [HuggingFace](https://huggingface.co/models?library=sentence-transformers)
2. Add to MODEL_ZOO in `modules/semantic_clustering.py`
3. Test with your specific keyword domain

### **Fine-Tuning for Your Domain**

For specialized domains (medical, legal, technical):

1. Collect domain-specific text data
2. Fine-tune a base model using sentence-transformers
3. Use the custom model for better domain-specific clustering

### **Batch Processing Large Lists**

For millions of keywords:

1. Split into batches of 50,000-100,000 keywords
2. Process each batch separately
3. Combine results programmatically
4. Use the fastest models for large-scale processing

---

## Integration with Other Features

### **Data Analysis Tab**

Semantic clustering results are automatically available in the Data Analysis tab for:
- Cluster size distribution analysis
- Export to various formats
- Further processing and filtering

### **Comparison with SERP Clustering**

You can run both semantic and SERP clustering on the same keywords to:
- Compare clustering approaches
- Validate semantic clusters against SERP data
- Choose the best approach for your use case

---

## Best Practices

### **1. Model Selection**
- Start with gte-large or bge-large for most use cases
- Upgrade to larger models if quality is insufficient
- Consider your hardware limitations

### **2. Parameter Tuning**
- Start with default settings (0.95 threshold, size 2)
- Adjust based on your specific needs
- Test with a small sample first

### **3. Keyword Preparation**
- Remove duplicates and irrelevant keywords
- Ensure consistent formatting
- Consider keyword length and complexity

### **4. Result Validation**
- Review sample clusters manually
- Adjust parameters based on results
- Compare with domain expertise

### **5. Performance Monitoring**
- Monitor GPU/CPU usage
- Track processing times
- Optimize based on your typical workload

---

## Cost Analysis

### **Semantic Clustering Costs**
- **Setup**: One-time model download (2-10GB)
- **Processing**: Only electricity/hardware costs
- **Scaling**: No additional costs for more keywords

### **SERP Clustering Costs (Comparison)**
- **Per Keyword**: $0.50+ API costs
- **1,000 keywords**: ~$500
- **10,000 keywords**: ~$5,000
- **100,000 keywords**: ~$50,000

### **Break-Even Analysis**
Semantic clustering pays for itself after processing just a few thousand keywords, making it ideal for large-scale keyword research projects.
