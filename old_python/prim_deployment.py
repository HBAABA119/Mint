"""
Prim Model Deployment
Provides model serving, API generation, containerization, monitoring,
and A/B testing capabilities.
"""

import json
import pickle
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class DeploymentType(Enum):
    """Deployment types"""
    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    SERVERLESS = "serverless"
    EDGE = "edge"


class ModelFormat(Enum):
    """Model formats"""
    PICKLE = "pickle"
    ONNX = "onnx"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    PRIM = "prim"


@dataclass
class Model:
    """Model for deployment"""
    name: str
    version: str
    model: Any
    format: ModelFormat
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Deployment:
    """Model deployment"""
    id: str
    model: Model
    deployment_type: DeploymentType
    endpoint: str
    status: str = "pending"
    metrics: Dict[str, Any] = field(default_factory=dict)


class ModelServer:
    """Model server for serving predictions"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.models: Dict[str, Model] = {}
        self.running = False

    def load_model(self, model: Model):
        """Load model into server"""
        self.models[model.name] = model

    def unload_model(self, name: str):
        """Unload model from server"""
        if name in self.models:
            del self.models[name]

    def predict(self, model_name: str, data: Any) -> Any:
        """Make prediction"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")

        model = self.models[model_name]

        if hasattr(model.model, 'predict'):
            return model.model.predict(data)
        else:
            # Simple function call
            return model.model(data)

    def start(self):
        """Start model server"""
        self.running = True
        print(f"Model server started on {self.host}:{self.port}")

    def stop(self):
        """Stop model server"""
        self.running = False
        print("Model server stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get server status"""
        return {
            "host": self.host,
            "port": self.port,
            "running": self.running,
            "models": list(self.models.keys())
        }


class APIGenerator:
    """API generator for model endpoints"""

    def __init__(self):
        self.endpoints: List[Dict[str, Any]] = []

    def generate_rest_api(self, model_name: str, input_schema: Dict[str, Any],
                         output_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate REST API specification"""
        api_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{model_name} API",
                "version": "1.0.0"
            },
            "paths": {
                f"/predict": {
                    "post": {
                        "summary": "Make prediction",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": input_schema
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": output_schema
                                    }
                                }
                            }
                        }
                    }
                },
                "/health": {
                    "get": {
                        "summary": "Health check",
                        "responses": {
                            "200": {
                                "description": "Healthy"
                            }
                        }
                    }
                },
                "/metrics": {
                    "get": {
                        "summary": "Get metrics",
                        "responses": {
                            "200": {
                                "description": "Metrics"
                            }
                        }
                    }
                }
            }
        }

        return api_spec

    def generate_grpc_api(self, model_name: str) -> str:
        """Generate gRPC API specification"""
        proto = f"""
syntax = "proto3";

service {model_name}Service {{
    rpc Predict(PredictRequest) returns (PredictResponse);
    rpc Health(HealthRequest) returns (HealthResponse);
}}

message PredictRequest {{
    repeated float features = 1;
}}

message PredictResponse {{
    repeated float predictions = 1;
}}

message HealthRequest {{}}

message HealthResponse {{
    string status = 1;
}}
"""
        return proto


class Containerizer:
    """Containerization utilities"""

    def __init__(self):
        self.dockerfiles: List[Dict[str, Any]] = []

    def generate_dockerfile(self, model_name: str, python_version: str = "3.9",
                           dependencies: Optional[List[str]] = None) -> str:
        """Generate Dockerfile"""
        deps = dependencies or ["numpy", "scikit-learn", "flask"]

        dockerfile = f"""FROM python:{python_version}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY model/ ./model/
COPY app.py .

EXPOSE 8000

CMD ["python", "app.py"]
"""
        return dockerfile

    def generate_docker_compose(self, services: List[Dict[str, Any]]) -> str:
        """Generate docker-compose.yml"""
        compose = {
            "version": "3.8",
            "services": {}
        }

        for i, service in enumerate(services):
            compose["services"][f"service_{i}"] = {
                "build": service.get("build", "."),
                "ports": [f"{service.get('port', 8000)}:8000"],
                "environment": service.get("environment", {}),
                "volumes": service.get("volumes", [])
            }

        return json.dumps(compose, indent=2)


class DeploymentMonitor:
    """Deployment monitoring"""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.alerts: List[Dict[str, Any]] = []

    def record_metric(self, name: str, value: float):
        """Record metric value"""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)

    def get_metrics(self, name: str) -> List[float]:
        """Get metric history"""
        return self.metrics.get(name, [])

    def add_alert(self, severity: str, message: str):
        """Add alert"""
        self.alerts.append({
            "severity": severity,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

    def get_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get alerts"""
        if severity:
            return [a for a in self.alerts if a["severity"] == severity]
        return self.alerts.copy()


class ABTestManager:
    """A/B testing management"""

    def __init__(self):
        self.experiments: Dict[str, Dict[str, Any]] = {}
        self.assignments: Dict[str, str] = {}

    def create_experiment(self, name: str, variants: List[str],
                        traffic_split: Optional[List[float]] = None):
        """Create A/B test experiment"""
        if traffic_split is None:
            traffic_split = [1.0 / len(variants)] * len(variants)

        self.experiments[name] = {
            "variants": variants,
            "traffic_split": traffic_split,
            "metrics": {}
        }

    def assign_variant(self, experiment_name: str, user_id: str) -> str:
        """Assign user to variant"""
        if experiment_name not in self.experiments:
            return "control"

        # Check if already assigned
        key = f"{experiment_name}:{user_id}"
        if key in self.assignments:
            return self.assignments[key]

        # Assign to variant based on traffic split
        import random
        experiment = self.experiments[experiment_name]
        variants = experiment["variants"]
        traffic_split = experiment["traffic_split"]

        r = random.random()
        cumulative = 0.0
        for i, split in enumerate(traffic_split):
            cumulative += split
            if r < cumulative:
                variant = variants[i]
                self.assignments[key] = variant
                return variant

        return variants[-1]

    def record_metric(self, experiment_name: str, variant: str,
                     metric_name: str, value: float):
        """Record metric for variant"""
        if experiment_name not in self.experiments:
            return

        experiment = self.experiments[experiment_name]
        if variant not in experiment["metrics"]:
            experiment["metrics"][variant] = {}

        if metric_name not in experiment["metrics"][variant]:
            experiment["metrics"][variant][metric_name] = []

        experiment["metrics"][variant][metric_name].append(value)

    def get_results(self, experiment_name: str) -> Dict[str, Any]:
        """Get experiment results"""
        if experiment_name not in self.experiments:
            return {}

        experiment = self.experiments[experiment_name]
        results = {}

        for variant, metrics in experiment["metrics"].items():
            results[variant] = {}
            for metric_name, values in metrics.items():
                if values:
                    results[variant][metric_name] = {
                        "mean": sum(values) / len(values),
                        "count": len(values)
                    }

        return results


class DeploymentPipeline:
    """Deployment pipeline"""

    def __init__(self):
        self.stages: List[str] = []
        self.status = "idle"

    def add_stage(self, name: str, action: Callable):
        """Add pipeline stage"""
        self.stages.append({"name": name, "action": action})

    def run(self) -> Dict[str, Any]:
        """Run deployment pipeline"""
        results = []
        self.status = "running"

        for stage in self.stages:
            try:
                result = stage["action"]()
                results.append({
                    "stage": stage["name"],
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                results.append({
                    "stage": stage["name"],
                    "status": "failed",
                    "error": str(e)
                })
                self.status = "failed"
                break

        if self.status == "running":
            self.status = "completed"

        return {
            "status": self.status,
            "stages": results
        }


class ModelRegistry:
    """Model registry for version management"""

    def __init__(self):
        self.models: Dict[str, List[Model]] = {}

    def register_model(self, model: Model):
        """Register model in registry"""
        if model.name not in self.models:
            self.models[model.name] = []
        self.models[model.name].append(model)

    def get_model(self, name: str, version: Optional[str] = None) -> Optional[Model]:
        """Get model from registry"""
        if name not in self.models:
            return None

        models = self.models[name]

        if version:
            for model in models:
                if model.version == version:
                    return model
        else:
            # Return latest version
            return models[-1]

        return None

    def list_models(self) -> List[str]:
        """List all models"""
        return list(self.models.keys())

    def list_versions(self, name: str) -> List[str]:
        """List versions of a model"""
        if name not in self.models:
            return []
        return [m.version for m in self.models[name]]


def create_deployment(model: Model, deployment_type: DeploymentType,
                    endpoint: str) -> Deployment:
    """Create deployment"""
    return Deployment(
        id=f"deploy_{datetime.now().timestamp()}",
        model=model,
        deployment_type=deployment_type,
        endpoint=endpoint
    )


def main():
    """Main entry point for testing"""
    print("Testing Model Deployment...")

    # Test Model Server
    server = ModelServer(host="localhost", port=8000)

    # Create a simple model
    class SimpleModel:
        def predict(self, data):
            return [x * 2 for x in data]

    model = Model(
        name="test_model",
        version="1.0",
        model=SimpleModel(),
        format=ModelFormat.PRIM
    )

    server.load_model(model)
    server.start()

    # Test prediction
    prediction = server.predict("test_model", [1, 2, 3, 4, 5])
    print(f"Prediction: {prediction}")

    server.stop()

    # Test API Generator
    api_gen = APIGenerator()
    input_schema = {"type": "object", "properties": {"features": {"type": "array"}}}
    output_schema = {"type": "object", "properties": {"predictions": {"type": "array"}}}

    api_spec = api_gen.generate_rest_api("test_model", input_schema, output_schema)
    print(f"API spec: {len(api_spec)} lines")

    # Test Containerizer
    containerizer = Containerizer()
    dockerfile = containerizer.generate_dockerfile("test_model")
    print(f"Dockerfile: {len(dockerfile)} characters")

    # Test Deployment Monitor
    monitor = DeploymentMonitor()
    monitor.record_metric("response_time", 0.5)
    monitor.record_metric("response_time", 0.6)
    monitor.add_alert("warning", "High response time")
    print(f"Metrics: {monitor.get_metrics('response_time')}")
    print(f"Alerts: {len(monitor.get_alerts())}")

    # Test AB Test Manager
    ab_test = ABTestManager()
    ab_test.create_experiment("test_exp", ["control", "variant_a", "variant_b"])
    variant = ab_test.assign_variant("test_exp", "user1")
    print(f"Assigned variant: {variant}")

    ab_test.record_metric("test_exp", "control", "conversion", 1.0)
    ab_test.record_metric("test_exp", "control", "conversion", 0.0)
    results = ab_test.get_results("test_exp")
    print(f"Experiment results: {results}")

    # Test Deployment Pipeline
    pipeline = DeploymentPipeline()
    pipeline.add_stage("build", lambda: "Build complete")
    pipeline.add_stage("test", lambda: "Tests passed")
    pipeline.add_stage("deploy", lambda: "Deployed")

    pipeline_results = pipeline.run()
    print(f"Pipeline status: {pipeline_results['status']}")

    # Test Model Registry
    registry = ModelRegistry()
    registry.register_model(model)
    registered = registry.get_model("test_model")
    print(f"Registered model: {registered.name if registered else 'None'}")

    print("\nModel Deployment initialized successfully")


if __name__ == "__main__":
    main()
