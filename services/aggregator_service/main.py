from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
import psycopg2
import logging
from typing import List, Dict, Optional
from config import Config
import traceback

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataAggregator:
    def __init__(self):
        self._init_mongo_connection()
        self._init_redshift_connection()

    def _init_mongo_connection(self):
        """Initialize MongoDB connection with error handling"""
        try:
            logger.info("Connecting to MongoDB...")
            self.mongo_client = MongoClient(Config.MONGO_URL)
            self.mongo_db = self.mongo_client[Config.MONGO_DB]
            # Test the connection
            self.mongo_client.server_info()
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def _init_redshift_connection(self):
        """Initialize Redshift connection with error handling"""
        try:
            logger.info("Connecting to Redshift...")
            self.redshift_conn = psycopg2.connect(
                dbname=Config.REDSHIFT_DB,
                host=Config.REDSHIFT_HOST,
                port=Config.REDSHIFT_PORT,
                user=Config.REDSHIFT_USER,
                password=Config.REDSHIFT_PASSWORD
            )
            logger.info("Successfully connected to Redshift")
            self.create_redshift_tables()
        except Exception as e:
            logger.error(f"Failed to connect to Redshift: {str(e)}")
            raise

    def create_redshift_tables(self):
        """Create necessary tables in Redshift if they don't exist"""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS doctor_appointments_agg (
                doctor_id VARCHAR(255),
                doctor_name VARCHAR(255),
                specialty VARCHAR(255),
                appointment_count INTEGER,
                aggregation_date DATE,
                PRIMARY KEY (doctor_id, aggregation_date)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS appointment_frequency_agg (
                date DATE,
                appointment_count INTEGER,
                aggregation_date DATE,
                PRIMARY KEY (date, aggregation_date)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS symptoms_by_specialty_agg (
                specialty VARCHAR(255),
                symptom VARCHAR(255),
                occurrence_count INTEGER,
                aggregation_date DATE,
                PRIMARY KEY (specialty, symptom, aggregation_date)
            )
            """
        ]

        cursor = None
        try:
            cursor = self.redshift_conn.cursor()
            for query in queries:
                cursor.execute(query)
            self.redshift_conn.commit()
            logger.info("Successfully created/verified Redshift tables")
        except Exception as e:
            logger.error(f"Failed to create Redshift tables: {str(e)}")
            if self.redshift_conn:
                self.redshift_conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def _get_doctor_info(self, doctor_id: str) -> Optional[Dict]:
        """Helper method to get doctor information"""
        try:
            return self.mongo_db.doctors.find_one({"_id": ObjectId(doctor_id)})
        except Exception as e:
            logger.error(f"Error retrieving doctor info for ID {doctor_id}: {str(e)}")
            return None

    def aggregate_doctor_appointments(self) -> List[Dict]:
        """Aggregate appointments per doctor"""
        logger.info("Starting doctor appointments aggregation")
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$doctor_id",
                        "appointment_count": {"$sum": 1}
                    }
                }
            ]

            appointments_result = list(self.mongo_db.appointments.aggregate(pipeline))
            logger.info(f"Found {len(appointments_result)} doctor appointment records")

            aggregated_data = []
            for appointment in appointments_result:
                doctor_id = appointment["_id"]
                doctor = self._get_doctor_info(doctor_id)

                aggregated_data.append({
                    "doctor_id": str(doctor_id),
                    "doctor_name": doctor.get("name", "Unknown") if doctor else "Unknown",
                    "specialty": doctor.get("specialty", "Unknown") if doctor else "Unknown",
                    "appointment_count": appointment["appointment_count"]
                })

            logger.info(f"Successfully aggregated {len(aggregated_data)} doctor records")
            return aggregated_data

        except Exception as e:
            logger.error(f"Error in doctor appointments aggregation: {str(e)}")
            logger.error(traceback.format_exc())
            return []

    def aggregate_appointment_frequency(self) -> List[Dict]:
        """Aggregate appointment frequency over time"""
        logger.info("Starting appointment frequency aggregation")
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$appointment_date",
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}}
            ]

            result = list(self.mongo_db.appointments.aggregate(pipeline))
            logger.info(f"Successfully aggregated {len(result)} frequency records")

            return [
                {
                    "date": r["_id"],
                    "appointment_count": r["count"]
                }
                for r in result
            ]
        except Exception as e:
            logger.error(f"Error in appointment frequency aggregation: {str(e)}")
            logger.error(traceback.format_exc())
            return []

    def aggregate_symptoms_by_specialty(self) -> List[Dict]:
        """Aggregate symptoms categorized by specialty"""
        logger.info("Starting symptoms by specialty aggregation")
        try:
            pipeline = [
                {
                    "$addFields": {
                        "doctor_object_id": {
                            "$toObjectId": "$doctor_id"
                        }
                    }
                },
                {
                    "$lookup": {
                        "from": "doctors",
                        "localField": "doctor_object_id",
                        "foreignField": "_id",
                        "as": "doctor_info"
                    }
                },
                {"$unwind": "$doctor_info"},
                {"$unwind": "$symptoms"},
                {
                    "$group": {
                        "_id": {
                            "specialty": "$doctor_info.specialty",
                            "symptom": "$symptoms"
                        },
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"count": -1}},
                {
                    "$project": {
                        "_id": 0,
                        "specialty": "$_id.specialty",
                        "symptom": "$_id.symptom",
                        "occurrence_count": "$count"
                    }
                }
            ]

            result = list(self.mongo_db.appointments.aggregate(pipeline))
            logger.info(f"Successfully aggregated {len(result)} symptom records")
            return result

        except Exception as e:
            logger.error(f"Error in symptoms aggregation: {str(e)}")
            logger.error(traceback.format_exc())
            return []

    def save_to_redshift(self, data: List[Dict], table_name: str, columns: List[str]):
        """Save aggregated data to Redshift"""
        if not data:
            logger.warning(f"No data to save for table {table_name}")
            return

        logger.info(f"Saving {len(data)} records to {table_name}")
        cursor = None
        try:
            cursor = self.redshift_conn.cursor()
            values_template = "(" + ",".join(["%s"] * len(columns)) + ")"
            query = f"""
                INSERT INTO {table_name} 
                ({','.join(columns)}) 
                VALUES {values_template}
            """

            for item in data:
                values = [item[col] for col in columns[:-1]]
                values.append(datetime.now().date())
                cursor.execute(query, values)

            self.redshift_conn.commit()
            logger.info(f"Successfully saved data to {table_name}")

        except Exception as e:
            logger.error(f"Error saving to Redshift table {table_name}: {str(e)}")
            logger.error(traceback.format_exc())
            if self.redshift_conn:
                self.redshift_conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def run_aggregation(self):
        """Run all aggregations and save to Redshift"""
        logger.info("Starting data aggregation process")
        try:
            # Aggregate and save doctor appointments
            doctor_appointments = self.aggregate_doctor_appointments()
            print("doctor_appointments :",doctor_appointments)
            self.save_to_redshift(
                doctor_appointments,
                "doctor_appointments_agg",
                ["doctor_id", "doctor_name", "specialty", "appointment_count", "aggregation_date"]
            )

            # Aggregate and save appointment frequency
            appointment_freq = self.aggregate_appointment_frequency()
            print("appointment_freq :",appointment_freq)
            self.save_to_redshift(
                appointment_freq,
                "appointment_frequency_agg",
                ["date", "appointment_count", "aggregation_date"]
            )

            # Aggregate and save symptoms by specialty
            symptoms_specialty = self.aggregate_symptoms_by_specialty()
            print("symptoms_specialty :",symptoms_specialty)
            self.save_to_redshift(
                symptoms_specialty,
                "symptoms_by_specialty_agg",
                ["specialty", "symptom", "occurrence_count", "aggregation_date"]
            )

            logger.info("Data aggregation completed successfully")

        except Exception as e:
            logger.error(f"Error during aggregation process: {str(e)}")
            logger.error(traceback.format_exc())
            raise
        finally:
            self._cleanup()

    def _cleanup(self):
        """Cleanup database connections"""
        try:
            if hasattr(self, 'mongo_client'):
                self.mongo_client.close()
            if hasattr(self, 'redshift_conn'):
                self.redshift_conn.close()
            logger.info("Cleaned up database connections")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

if __name__ == "__main__":
    try:
        aggregator = DataAggregator()
        aggregator.run_aggregation()
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        logger.error(traceback.format_exc())