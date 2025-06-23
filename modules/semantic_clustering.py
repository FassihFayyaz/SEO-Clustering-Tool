# modules/semantic_clustering.py

import pandas as pd
import time
from typing import List, Dict, Optional

try:
    import torch
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    TensorType = torch.Tensor
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    TensorType = None
    # Create dummy classes to prevent import errors
    class torch:
        Tensor = None

        @staticmethod
        def cuda():
            class cuda:
                @staticmethod
                def is_available():
                    return False
                @staticmethod
                def get_device_name(_):
                    return "N/A"
            return cuda()

        @staticmethod
        def tensor(_):
            return None

    class SentenceTransformer:
        pass

    class util:
        @staticmethod
        def community_detection(*_, **__):
            _ = __  # Ignore unused kwargs
            return []

class SemanticClusteringEngine:
    """
    Semantic clustering engine for keyword clustering using embedding models.
    Supports multiple pre-trained models and flexible clustering parameters.
    """
    
    # Model zoo with popular embedding models
    MODEL_ZOO = {
        'Recommended (Rank 3) - 10GB+ VRAM - Qwen3-Embedding-4B': 'Qwen/Qwen3-Embedding-4B',
        'Fastest (Rank 4) - 4GB+ VRAM - Qwen3-Embedding-0.6B': 'Qwen/Qwen3-Embedding-0.6B',
        'Top Tier (Rank 2) - 20GB+ VRAM - Qwen3-Embedding-8B': 'Qwen/Qwen3-Embedding-8B',
        'Balanced (CPU/GPU) - 2GB+ VRAM - gte-large': 'thenlper/gte-large',
        'Balanced (CPU/GPU) - 2GB+ VRAM - bge-large-en-v1.5': 'BAAI/bge-large-en-v1.5',
        'High Quality XL - 5GB+ VRAM - sentence-t5-xl': 'sentence-transformers/sentence-t5-xl',
    }
    
    def __init__(self):
        """Initialize the semantic clustering engine."""
        self.model = None
        self.device = None
        self.model_name = None
        
    def check_dependencies(self) -> bool:
        """Check if required dependencies are available."""
        return SENTENCE_TRANSFORMERS_AVAILABLE
    
    def get_available_models(self) -> Dict[str, str]:
        """Get the available embedding models."""
        return self.MODEL_ZOO.copy()
    
    def detect_device(self) -> str:
        """Detect the best available device (CUDA or CPU)."""
        if torch.cuda.is_available():
            device = 'cuda'
            gpu_name = torch.cuda.get_device_name(0)
            return device, gpu_name
        else:
            return 'cpu', 'CPU'
    
    def load_model(self, model_key: str, progress_callback=None) -> bool:
        """
        Load the specified embedding model.
        
        Args:
            model_key: Key from MODEL_ZOO
            progress_callback: Optional callback for progress updates
            
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        if not self.check_dependencies():
            return False
            
        try:
            if model_key not in self.MODEL_ZOO:
                raise ValueError(f"Model key '{model_key}' not found in MODEL_ZOO")
            
            model_name = self.MODEL_ZOO[model_key]
            self.device, device_info = self.detect_device()
            
            if progress_callback:
                progress_callback(f"Loading model: {model_name}")
                progress_callback(f"Using device: {device_info}")
            
            # Configure model loading parameters
            model_kwargs = {'trust_remote_code': True}
            
            # Use optimized loading for large models on GPU
            if self.device == 'cuda' and any(tag in model_name for tag in ['4B', '7B', '8B']):
                if progress_callback:
                    progress_callback("Large model detected on GPU. Using optimized loading...")
                model_kwargs['device_map'] = "auto"
                model_kwargs['torch_dtype'] = torch.bfloat16
                model_kwargs['low_cpu_mem_usage'] = True
                device_param = None
            else:
                device_param = self.device
            
            # Load the model
            self.model = SentenceTransformer(
                model_name,
                device=device_param,
                model_kwargs=model_kwargs
            )
            
            self.model_name = model_name
            
            if progress_callback:
                progress_callback(f"✅ Model loaded successfully: {model_key}")
            
            return True
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ Error loading model: {str(e)}")
            return False
    
    def generate_embeddings(self, keywords: List[str], progress_callback=None) -> Optional[TensorType]:
        """
        Generate embeddings for the given keywords.
        
        Args:
            keywords: List of keywords to embed
            progress_callback: Optional callback for progress updates
            
        Returns:
            torch.Tensor: Embeddings tensor or None if failed
        """
        if self.model is None:
            if progress_callback:
                progress_callback("❌ No model loaded. Please load a model first.")
            return None
        
        try:
            if progress_callback:
                progress_callback(f"Generating embeddings for {len(keywords)} keywords...")
            
            # Use prompt_name for Qwen models
            prompt_name = "query" if 'Qwen' in self.model_name else None
            
            embeddings = self.model.encode(
                keywords,
                show_progress_bar=False,  # We'll handle progress ourselves
                prompt_name=prompt_name
            )
            
            if progress_callback:
                progress_callback("✅ Embeddings generated successfully")
            
            return torch.tensor(embeddings)
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ Error generating embeddings: {str(e)}")
            return None
    
    def perform_clustering(self, embeddings: TensorType, similarity_threshold: float = 0.95,
                          min_cluster_size: int = 2, progress_callback=None) -> List[List[int]]:
        """
        Perform semantic clustering on the embeddings.
        
        Args:
            embeddings: Tensor of keyword embeddings
            similarity_threshold: Similarity threshold for clustering (0.1 to 1.0)
            min_cluster_size: Minimum number of keywords per cluster
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of clusters, where each cluster is a list of keyword indices
        """
        try:
            if progress_callback:
                progress_callback("Performing semantic clustering...")
            
            # Move embeddings to CPU for clustering
            embeddings_cpu = embeddings.to('cpu')
            
            # Perform community detection clustering
            clusters = util.community_detection(
                embeddings_cpu,
                min_community_size=min_cluster_size,
                threshold=similarity_threshold
            )
            
            if progress_callback:
                progress_callback(f"✅ Found {len(clusters)} clusters")
            
            return clusters
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ Error during clustering: {str(e)}")
            return []
    
    def format_clusters(self, keywords: List[str], clusters: List[List[int]]) -> pd.DataFrame:
        """
        Format clusters into a parent-child DataFrame.
        
        Args:
            keywords: Original list of keywords
            clusters: List of clusters (each cluster is a list of indices)
            
        Returns:
            pd.DataFrame: Formatted clusters with Parent and Child keywords
        """
        output_rows = []
        keyword_map = {i: keyword for i, keyword in enumerate(keywords)}
        
        for cluster in clusters:
            if not cluster:
                continue
                
            # Use the first keyword (lowest index) as the parent
            parent_index = min(cluster)
            parent_keyword = keyword_map[parent_index]
            
            for keyword_index in cluster:
                child_keyword = keyword_map[keyword_index]
                output_rows.append({
                    'Parent Keyword': parent_keyword,
                    'Child Keyword': child_keyword,
                    'Cluster Size': len(cluster)
                })
        
        if not output_rows:
            return pd.DataFrame([], columns=['Parent Keyword', 'Child Keyword', 'Cluster Size'])
        
        return pd.DataFrame(output_rows)
    
    def cluster_keywords(self, keywords: List[str], model_key: str, similarity_threshold: float = 0.95,
                        min_cluster_size: int = 2, progress_callback=None) -> Optional[pd.DataFrame]:
        """
        Complete clustering workflow: load model, generate embeddings, cluster, and format results.
        
        Args:
            keywords: List of keywords to cluster
            model_key: Model to use from MODEL_ZOO
            similarity_threshold: Similarity threshold for clustering
            min_cluster_size: Minimum cluster size
            progress_callback: Optional callback for progress updates
            
        Returns:
            pd.DataFrame: Formatted clustering results or None if failed
        """
        start_time = time.time()
        
        try:
            # Step 1: Load model
            if not self.load_model(model_key, progress_callback):
                return None
            
            # Step 2: Generate embeddings
            embeddings = self.generate_embeddings(keywords, progress_callback)
            if embeddings is None:
                return None
            
            # Step 3: Perform clustering
            clusters = self.perform_clustering(
                embeddings, similarity_threshold, min_cluster_size, progress_callback
            )
            
            # Step 4: Format results
            if progress_callback:
                progress_callback("Formatting results...")
            
            results_df = self.format_clusters(keywords, clusters)
            
            end_time = time.time()
            if progress_callback:
                progress_callback(f"✅ Clustering complete! Total time: {end_time - start_time:.2f} seconds")
            
            return results_df
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ Clustering failed: {str(e)}")
            return None
