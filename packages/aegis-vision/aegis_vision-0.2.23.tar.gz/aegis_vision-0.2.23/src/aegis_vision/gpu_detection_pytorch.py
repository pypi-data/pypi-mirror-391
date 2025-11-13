"""
PyTorch GPU detection module.

Detects CUDA and MPS acceleration via PyTorch CUDA API.
This is the primary detection method when PyTorch is available.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PyTorchGPUDetector:
    """
    PyTorch-based GPU detection.
    
    Works with both CUDA (NVIDIA) and MPS (Apple Silicon) backends.
    """
    
    @staticmethod
    def detect_cuda() -> Dict[str, Any]:
        """
        Detect NVIDIA CUDA GPUs via PyTorch.
        
        Returns:
            Dict with CUDA GPU info
        """
        result = {
            "available": False,
            "version": None,
            "device_count": 0,
            "devices": [],
            "error": None
        }
        
        try:
            import torch
            
            if not torch.cuda.is_available():
                result["error"] = "torch.cuda.is_available() returned False"
                logger.debug(result["error"])
                return result
            
            result["available"] = True
            result["version"] = torch.version.cuda
            result["device_count"] = torch.cuda.device_count()
            
            for i in range(result["device_count"]):
                try:
                    props = torch.cuda.get_device_properties(i)
                    device_name = torch.cuda.get_device_name(i)
                    total_memory = torch.cuda.get_device_properties(i).total_memory
                    
                    device_info = {
                        "index": i,
                        "name": device_name,
                        "memory": round(total_memory / (1024**3), 2),  # Convert to GB
                        "compute_capability": f"{props.major}.{props.minor}",
                        "multi_processor_count": props.multi_processor_count,
                        "total_memory_bytes": total_memory
                    }
                    
                    result["devices"].append(device_info)
                    
                except Exception as e:
                    logger.debug(f"Failed to get device {i} properties: {e}")
                    
        except ImportError:
            result["error"] = "PyTorch not installed"
            logger.debug(result["error"])
        except Exception as e:
            result["error"] = str(e)
            logger.debug(f"CUDA detection failed: {e}")
        
        return result
    
    @staticmethod
    def detect_mps() -> Dict[str, Any]:
        """
        Detect Apple Metal Performance Shaders (MPS) via PyTorch.
        
        MPS is available on Apple Silicon Macs with PyTorch 1.12+.
        
        Returns:
            Dict with MPS info
        """
        result = {
            "available": False,
            "reason": None,
            "pytorch_supported": False,
            "version": None
        }
        
        try:
            import torch
            
            if not hasattr(torch.backends, 'mps'):
                result["reason"] = "PyTorch version doesn't support MPS"
                logger.debug(result["reason"])
                return result
            
            result["pytorch_supported"] = True
            
            if not torch.backends.mps.is_available():
                result["reason"] = "MPS is not available on this system"
                logger.debug(result["reason"])
                return result
            
            result["available"] = True
            result["reason"] = "MPS is available and ready to use"
            
            # Try to get MPS version info
            try:
                if hasattr(torch.backends.mps, 'version'):
                    result["version"] = torch.backends.mps.version()
            except Exception:
                pass
                
        except ImportError:
            result["reason"] = "PyTorch not installed"
            logger.debug(result["reason"])
        except Exception as e:
            result["reason"] = str(e)
            logger.debug(f"MPS detection failed: {e}")
        
        return result
    
    @staticmethod
    def get_optimal_device() -> Dict[str, Any]:
        """
        Determine the optimal device for training.
        
        Priority: CUDA > MPS > CPU
        
        Returns:
            Dict with optimal device info
        """
        result = {
            "device": "cpu",
            "device_name": "CPU",
            "reason": "Using CPU fallback",
            "priority": 0
        }
        
        try:
            # Try CUDA first
            cuda_info = PyTorchGPUDetector.detect_cuda()
            if cuda_info["available"] and cuda_info["devices"]:
                primary_gpu = cuda_info["devices"][0]
                result["device"] = "cuda"
                result["device_name"] = primary_gpu["name"]
                result["reason"] = f"CUDA available: {primary_gpu['name']}"
                result["priority"] = 100
                result["cuda_info"] = cuda_info
                return result
            
            # Try MPS
            mps_info = PyTorchGPUDetector.detect_mps()
            if mps_info["available"]:
                result["device"] = "mps"
                result["device_name"] = "Apple Metal (MPS)"
                result["reason"] = "MPS available (Apple Silicon)"
                result["priority"] = 50
                result["mps_info"] = mps_info
                return result
            
        except Exception as e:
            logger.debug(f"Error determining optimal device: {e}")
        
        return result
    
    @staticmethod
    def detect() -> Dict[str, Any]:
        """
        Complete PyTorch GPU detection.
        
        Returns:
            Dict with all GPU/accelerator info
        """
        return {
            "cuda": PyTorchGPUDetector.detect_cuda(),
            "mps": PyTorchGPUDetector.detect_mps(),
            "optimal_device": PyTorchGPUDetector.get_optimal_device()
        }
    
    @staticmethod
    def print_pytorch_info():
        """Print detailed PyTorch GPU information."""
        try:
            import torch
            print(f"PyTorch version: {torch.__version__}")
            print(f"CUDA available: {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                print(f"CUDA version: {torch.version.cuda}")
                print(f"GPU count: {torch.cuda.device_count()}")
                for i in range(torch.cuda.device_count()):
                    print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
        except ImportError:
            print("PyTorch not installed")
        except Exception as e:
            print(f"Error printing PyTorch info: {e}")

