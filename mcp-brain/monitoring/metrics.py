from prometheus_client import Counter, Histogram

class Metrics:
    def __init__(self):
        self.pipeline_runs = Counter('pipeline_runs_total', 'Total number of pipeline runs')
        self.pipeline_success = Counter('pipeline_success_total', 'Total successful pipeline runs')
        self.pipeline_failure = Counter('pipeline_failure_total', 'Total failed pipeline runs')
        
        self.scrape_success = Counter('scrape_success_total', 'Total successful scrapes')
        self.llm_analysis_time = Histogram('llm_analysis_duration_seconds', 'LLM Analysis Time')
        self.brief_generation_count = Counter('brief_generation_total', 'Total number of generated design briefs')

        # Phase 3 — Template Generation Metrics
        self.template_generation_time = Histogram('template_generation_seconds', 'Template generation duration')
        self.template_component_count = Counter('template_components_total', 'Total components generated')
        self.template_validation_success = Counter('template_validation_success_total', 'Templates that passed validation')
        self.template_validation_failure = Counter('template_validation_failure_total', 'Templates that failed validation')
        self.template_preview_success = Counter('template_preview_success_total', 'Successful preview screenshots')
        self.template_packages_created = Counter('template_packages_total', 'Template zip packages created')

    def increment_pipeline_run(self):
        self.pipeline_runs.inc()
        
    def increment_pipeline_success(self):
        self.pipeline_success.inc()
        
    def increment_pipeline_failure(self):
        self.pipeline_failure.inc()

    def set_llm_time(self, duration: float):
        self.llm_analysis_time.observe(duration)

    def record_template_generation(self, duration: float, component_count: int, valid: bool, preview_ok: bool):
        """Record Phase 3 generation metrics in one call."""
        self.template_generation_time.observe(duration)
        self.template_component_count.inc(component_count)
        if valid:
            self.template_validation_success.inc()
        else:
            self.template_validation_failure.inc()
        if preview_ok:
            self.template_preview_success.inc()
        self.template_packages_created.inc()
        
metrics = Metrics()
