#!/usr/bin/env python3
"""
⚡ Universal Soul AI - Performance Benchmark
==========================================
Quick performance benchmark for key system components.
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from thinkmesh_core.automation.coact_integration import CoAct1AutomationEngine, EnhancedConfidenceCalculator
from thinkmesh_core.interfaces import UserContext
from thinkmesh_core.automation.gui_automation import AutomationPlatform

class PerformanceBenchmark:
    """Quick performance benchmark for Universal Soul AI"""
    
    def __init__(self):
        self.results = {}
    
    async def run_benchmark(self):
        """Run performance benchmark"""
        print("⚡ Universal Soul AI - Performance Benchmark")
        print("=" * 50)
        
        context = UserContext(
            user_id="benchmark_user",
            device_info={"device_type": "mobile", "os": "android"},
            session_data={"app_context": "benchmark"},
            preferences={"local_processing": True},
            privacy_settings={"local_processing_only": True}
        )
        
        # Benchmark tests
        await self._benchmark_engine_initialization()
        await self._benchmark_task_analysis(context)
        await self._benchmark_confidence_calculation(context)
        await self._benchmark_concurrent_operations(context)
        
        self._print_benchmark_results()
    
    async def _benchmark_engine_initialization(self):
        """Benchmark engine initialization time"""
        print("🚀 Benchmarking Engine Initialization...")
        
        times = []
        for i in range(5):
            start = time.time()
            engine = CoAct1AutomationEngine()
            times.append(time.time() - start)
        
        avg_time = statistics.mean(times)
        self.results['Engine Initialization'] = {
            'avg_time': avg_time,
            'min_time': min(times),
            'max_time': max(times),
            'unit': 'seconds'
        }
        
        print(f"   Average: {avg_time:.3f}s | Min: {min(times):.3f}s | Max: {max(times):.3f}s")
    
    async def _benchmark_task_analysis(self, context: UserContext):
        """Benchmark task analysis performance"""
        print("🧠 Benchmarking Task Analysis...")
        
        engine = CoAct1AutomationEngine()
        tasks = [
            "Open calculator",
            "Navigate to settings and enable notifications",
            "Process data file and generate report",
            "Automate complex multi-step workflow",
            "Handle error recovery scenario"
        ]
        
        times = []
        confidence_scores = []
        
        for task in tasks:
            start = time.time()
            analysis = await engine.orchestrator_agent.analyze_task_intelligently(
                task, context, AutomationPlatform.MOBILE
            )
            times.append(time.time() - start)
            confidence_scores.append(analysis.confidence_score)
        
        avg_time = statistics.mean(times)
        avg_confidence = statistics.mean(confidence_scores)
        
        self.results['Task Analysis'] = {
            'avg_time': avg_time,
            'avg_confidence': avg_confidence,
            'tasks_tested': len(tasks),
            'unit': 'seconds'
        }
        
        print(f"   Average: {avg_time:.3f}s | Confidence: {avg_confidence:.1%} | Tasks: {len(tasks)}")
    
    async def _benchmark_confidence_calculation(self, context: UserContext):
        """Benchmark confidence calculation performance"""
        print("🎯 Benchmarking Confidence Calculation...")
        
        calculator = EnhancedConfidenceCalculator()
        tasks = [
            "Simple click action",
            "Complex data processing task",
            "Multi-step automation workflow",
            "Voice command processing",
            "Error handling scenario"
        ]
        
        times = []
        confidence_scores = []
        
        for task in tasks:
            start = time.time()
            confidence = await calculator.calculate_confidence(
                task, context, AutomationPlatform.MOBILE
            )
            times.append(time.time() - start)
            confidence_scores.append(confidence)
        
        avg_time = statistics.mean(times)
        avg_confidence = statistics.mean(confidence_scores)
        
        self.results['Confidence Calculation'] = {
            'avg_time': avg_time,
            'avg_confidence': avg_confidence,
            'calculations': len(tasks),
            'unit': 'seconds'
        }
        
        print(f"   Average: {avg_time:.3f}s | Confidence: {avg_confidence:.1%} | Calculations: {len(tasks)}")
    
    async def _benchmark_concurrent_operations(self, context: UserContext):
        """Benchmark concurrent operations performance"""
        print("🔄 Benchmarking Concurrent Operations...")
        
        # Create concurrent tasks
        async def analyze_task(task_id: int):
            engine = CoAct1AutomationEngine()
            return await engine.orchestrator_agent.analyze_task_intelligently(
                f"Concurrent task {task_id}", context, AutomationPlatform.MOBILE
            )
        
        # Test with 10 concurrent operations
        start = time.time()
        tasks = [analyze_task(i) for i in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start
        
        successful_ops = sum(1 for r in results if not isinstance(r, Exception))
        throughput = successful_ops / total_time
        
        self.results['Concurrent Operations'] = {
            'total_time': total_time,
            'successful_ops': successful_ops,
            'total_ops': len(tasks),
            'throughput': throughput,
            'unit': 'ops/second'
        }
        
        print(f"   Total: {total_time:.3f}s | Success: {successful_ops}/{len(tasks)} | Throughput: {throughput:.1f} ops/s")
    
    def _print_benchmark_results(self):
        """Print benchmark summary"""
        print("\n" + "=" * 50)
        print("📊 PERFORMANCE BENCHMARK RESULTS")
        print("=" * 50)
        
        for test_name, metrics in self.results.items():
            print(f"\n🔹 {test_name}:")
            for metric, value in metrics.items():
                if metric != 'unit':
                    if isinstance(value, float):
                        if 'time' in metric:
                            print(f"   {metric}: {value:.3f}s")
                        elif 'confidence' in metric:
                            print(f"   {metric}: {value:.1%}")
                        elif 'throughput' in metric:
                            print(f"   {metric}: {value:.1f} ops/s")
                        else:
                            print(f"   {metric}: {value:.3f}")
                    else:
                        print(f"   {metric}: {value}")
        
        # Overall performance rating
        print(f"\n🏆 PERFORMANCE RATING:")
        print("-" * 30)
        
        # Calculate overall performance score
        engine_score = 1.0 if self.results['Engine Initialization']['avg_time'] < 1.0 else 0.5
        analysis_score = 1.0 if self.results['Task Analysis']['avg_time'] < 0.5 else 0.5
        confidence_score = 1.0 if self.results['Confidence Calculation']['avg_time'] < 0.2 else 0.5
        concurrent_score = 1.0 if self.results['Concurrent Operations']['throughput'] > 5.0 else 0.5
        
        overall_score = (engine_score + analysis_score + confidence_score + concurrent_score) / 4
        
        if overall_score >= 0.8:
            rating = "🟢 EXCELLENT"
        elif overall_score >= 0.6:
            rating = "🟡 GOOD"
        else:
            rating = "🔴 NEEDS IMPROVEMENT"
        
        print(f"Overall Performance: {rating} ({overall_score:.1%})")
        
        # Specific recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if self.results['Engine Initialization']['avg_time'] > 1.0:
            print("• Optimize engine initialization time")
        if self.results['Task Analysis']['avg_time'] > 0.5:
            print("• Improve task analysis performance")
        if self.results['Confidence Calculation']['avg_time'] > 0.2:
            print("• Optimize confidence calculation speed")
        if self.results['Concurrent Operations']['throughput'] < 5.0:
            print("• Enhance concurrent operation handling")
        
        if overall_score >= 0.8:
            print("• System performance is excellent!")
        
        print("=" * 50)


async def main():
    """Run performance benchmark"""
    benchmark = PerformanceBenchmark()
    await benchmark.run_benchmark()


if __name__ == "__main__":
    print("⚡ Starting Performance Benchmark...")
    try:
        asyncio.run(main())
        print("\n🎉 Benchmark completed successfully!")
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
