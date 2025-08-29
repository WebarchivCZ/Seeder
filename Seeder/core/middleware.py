import time
import sys
from django.utils.deprecation import MiddlewareMixin


class ProfilingMiddleware(MiddlewareMixin):
    """
    Middleware to profile the entire request/response cycle
    """

    def process_request(self, request):
        # Only profile POST requests to seeder URLs
        if request.method == 'POST' and '/seeder/' in request.path:
            request._profile_start = time.time()
            content_length = request.META.get('CONTENT_LENGTH', 'Unknown')
            print(f"\n{'🚀 REQUEST START':<20} | {request.method} {request.path}")
            print(f"{'Time':<20} | {time.strftime('%H:%M:%S')}")
            print(f"{'Content Length':<20} | {content_length} bytes")
            sys.stdout.flush()

    def process_view(self, request, view_func, view_args, view_kwargs):
        if hasattr(request, '_profile_start'):
            current_time = time.time()
            elapsed = current_time - request._profile_start
            print(f"{'🎯 VIEW START':<20} | {view_func.__name__} (+{elapsed:.2f}s)")

            # Check if files are available at this point
            if hasattr(request, 'FILES') and request.FILES:
                print(f"{'📁 FILES RECEIVED':<20} | {len(request.FILES)} files")
                for name, file_obj in request.FILES.items():
                    size = getattr(file_obj, 'size', 'Unknown')
                    print(f"{'  - File':<20} | {name}: {size} bytes")

            sys.stdout.flush()

    def process_template_response(self, request, response):
        if hasattr(request, '_profile_start'):
            current_time = time.time()
            elapsed = current_time - request._profile_start
            print(f"{'📄 TEMPLATE RENDER':<20} | (+{elapsed:.2f}s)")
            sys.stdout.flush()
        return response

    def process_response(self, request, response):
        if hasattr(request, '_profile_start'):
            response_start = time.time()
            total_time = response_start - request._profile_start
            print(
                f"{'✅ DJANGO DONE':<20} | Django processing: {total_time:.2f}s | Status: {response.status_code}")
            print(f"{'📤 RESPONSE START':<20} | Starting response transmission...")

            # Add response size info
            content_length = response.get('Content-Length', 'Unknown')
            print(f"{'📦 RESPONSE SIZE':<20} | Content-Length: {content_length}")

            # Mark when Django finishes and starts sending response
            response._django_response_start = response_start
            print(f"{'='*60}")
            sys.stdout.flush()
        return response
