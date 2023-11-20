from cachetools import cached, TTLCache

sample_metadata_cache = TTLCache(maxsize=5, ttl=int(60*60*0.5))
multiqc_cache = TTLCache(maxsize=5, ttl=int(60*60*0.5))
deseq_result_cache = TTLCache(maxsize=20, ttl=int(60*60*0.5))
s3_cache = TTLCache(maxsize=20, ttl=int(60*60*0.5))
sample_id_cache = TTLCache(maxsize=5, ttl=int(60*60*0.5))
ml_model_cache = TTLCache(maxsize=20, ttl=int(60*60*0.5))
