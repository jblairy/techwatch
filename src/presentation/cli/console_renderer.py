"""
Console Renderer - Presentation Layer
Hexagonal Architecture DDD
"""
from typing import List
from datetime import date

from ...domain.entities.post import Post
from ...domain.value_objects.date_range import DateRange


class ConsoleRenderer:
    """Console display of results - Presentation Layer"""

    def render_posts(self, source_name: str, posts: List[Post], date_range: DateRange) -> None:
        """Display posts from a source in the console"""
        print(f"\n📍 {source_name} ({date_range})")
        if posts:
            # Group posts by date
            posts_by_date = {}
            for post in posts:
                post_date = post.date or date.today()
                if post_date not in posts_by_date:
                    posts_by_date[post_date] = []
                posts_by_date[post_date].append(post)

            # Display by date (most recent to oldest)
            for post_date in sorted(posts_by_date.keys(), reverse=True):
                if len(posts_by_date) > 1:  # Display date only if there are multiple dates
                    print(f"  📅 {post_date}")

                for post in posts_by_date[post_date]:
                    print(f"  ✅ {post.title}")
                    print(f"  🔗 {post.url}")
                    if len(posts_by_date) == 1 and post.date:  # Display date if single date
                        print(f"  📅 {post.date}")
                print()  # Empty line between dates
        else:
            print("❌ No articles found in this period.")

    def render_fallback_alert(self, alert_message: str) -> None:
        """Display a fallback verification alert"""
        print(f"\n{alert_message}")

    def render_summary(self, total_posts: int, sources_count: int, date_range: DateRange) -> None:
        """Display a summary of the watch session"""
        print(f"\n📊 WATCH SUMMARY")
        print(f"Total articles found: {total_posts}")
        print(f"Sources crawled: {sources_count}")
        print(f"Period: {date_range}")

    def render_error(self, source_name: str, error_message: str) -> None:
        """Display an error for a specific source"""
        print(f"\n❌ Error with {source_name}: {error_message}")

    def render_no_data(self) -> None:
        """Display message when no data is available"""
        print("\n📭 No watch data available. Run the console service first to generate data.")

    def render_alert(self, source_name: str) -> None:
        """Affiche une alerte visuelle si aucun post n'est trouvé pour le crawler"""
        print(f"\n⚠️ Aucun article trouvé pour {source_name}. Veuillez vérifier le crawler, il est possiblement défectueux.")
