#!/usr/bin/env python3
"""
Clean up any phantom/test data from the database
"""

from app import create_app, db
from app.models import User, BigQueryProject, VPSInstance, DataSource

def main():
    app = create_app()
    with app.app_context():
        print("=== DATABASE CLEANUP ===")
        
        # Check current counts
        users_count = User.query.count()
        projects_count = BigQueryProject.query.count()
        vps_count = VPSInstance.query.count()
        sources_count = DataSource.query.count()
        
        print(f"Current counts:")
        print(f"  Users: {users_count}")
        print(f"  BigQuery Projects: {projects_count}")
        print(f"  VPS Instances: {vps_count}")
        print(f"  Data Sources: {sources_count}")
        
        # Clean up any phantom data
        if projects_count > 0:
            print(f"\n🧹 Cleaning up {projects_count} BigQuery projects...")
            BigQueryProject.query.delete()
            db.session.commit()
            print("✅ BigQuery projects cleaned")
        
        if vps_count > 0:
            print(f"\n🧹 Cleaning up {vps_count} VPS instances...")
            VPSInstance.query.delete()
            db.session.commit()
            print("✅ VPS instances cleaned")
        
        if sources_count > 0:
            print(f"\n🧹 Cleaning up {sources_count} data sources...")
            DataSource.query.delete()
            db.session.commit()
            print("✅ Data sources cleaned")
        
        # Final counts
        print(f"\n✅ Cleanup complete!")
        print(f"  Users: {User.query.count()}")
        print(f"  BigQuery Projects: {BigQueryProject.query.count()}")
        print(f"  VPS Instances: {VPSInstance.query.count()}")
        print(f"  Data Sources: {DataSource.query.count()}")

if __name__ == "__main__":
    main()
