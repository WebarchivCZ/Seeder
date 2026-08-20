import time
import cProfile
import pstats
import io
from functools import wraps
from django.conf import settings
import sys


def profile_view(func):
    """
    Decorator to profile Django views and print timing information directly to console
    This works even with redirects since output goes to stdout immediately
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Start timing
        start_time = time.time()

        # Always do detailed profiling for this function
        profiler = cProfile.Profile()
        profiler.enable()

        # Header with clear separation
        print(f"\n{'='*60}")
        print(f"🔍 PROFILING: {func.__name__}")
        print(f"Started at: {time.strftime('%H:%M:%S')}")
        print(f"{'='*60}")

        try:
            result = func(*args, **kwargs)
        finally:
            profiler.disable()
            end_time = time.time()
            total_time = end_time - start_time

            print(f"\n⏱️  TOTAL TIME: {total_time:.2f} seconds")

            # Create detailed profiling report
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s)
            ps.sort_stats('cumulative')
            ps.print_stats(30)  # Top 30 slowest functions

            profile_output = s.getvalue()

            print(f"\n📊 TOP SLOWEST FUNCTIONS:")
            print("-" * 60)
            # Parse and display the most relevant lines
            lines = profile_output.split('\n')
            for i, line in enumerate(lines):
                if 'ncalls' in line:  # Header line
                    print(line)
                    # Print next 25 lines (the actual function data)
                    for j in range(1, min(26, len(lines) - i)):
                        if i + j < len(lines) and lines[i + j].strip():
                            print(lines[i + j])
                    break

            print(f"{'='*60}")
            print(f"✅ PROFILING COMPLETE: {func.__name__} - {total_time:.2f}s")
            print(f"{'='*60}\n")

            # Force flush to ensure we see the output immediately
            sys.stdout.flush()

        return result
    return wrapper


def log_timing(label):
    """
    Context manager to time specific code blocks with immediate console output
    """
    class TimingContext:
        def __enter__(self):
            self.start = time.time()
            print(f"⏳ Starting: {label}")
            return self

        def __exit__(self, *args):
            duration = time.time() - self.start
            print(f"✅ Completed: {label} ({duration:.2f}s)")
            sys.stdout.flush()

    return TimingContext()
