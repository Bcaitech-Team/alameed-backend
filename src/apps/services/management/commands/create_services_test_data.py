from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from ...models import (
    UpholsteryMaterial,
    UpholsteryType,
    ServiceLocation,
    ServiceTimeSlot,
    UpholsteryBooking
)


class Command(BaseCommand):
    help = 'Creates test data for the upholstery service'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data for upholstery service...')

        with transaction.atomic():
            # Create upholstery materials
            self.create_materials()

            # Create upholstery types
            self.create_upholstery_types()

            # Create service locations
            self.create_service_locations()

            # Create time slots for the next 7 days
            self.create_time_slots()

            # Create sample bookings if there are vehicles
            self.create_sample_bookings()
            self.stdout.write(self.style.SUCCESS('Successfully created sample bookings!'))

            self.stdout.write(self.style.SUCCESS('Upholstery test data creation complete!'))

    def create_materials(self):
        """Create test upholstery materials"""
        materials = [
            {
                'name': 'Premium Leather',
                'description': 'Genuine high-quality leather with a smooth finish. Extremely durable and provides a luxurious feel.',
                'price_per_seat': Decimal('125.000'),
                'durability_rating': 5
            },
            {
                'name': 'Synthetic Leather',
                'description': 'High-grade synthetic leather that mimics the look and feel of genuine leather at a more affordable price.',
                'price_per_seat': Decimal('75.000'),
                'durability_rating': 4
            },
            {
                'name': 'Suede',
                'description': 'Soft, napped leather with a velvety texture. Adds a premium touch to your vehicle interior.',
                'price_per_seat': Decimal('110.000'),
                'durability_rating': 3
            },
            {
                'name': 'Microfiber',
                'description': 'Ultra-soft synthetic material that\'s resistant to stains and easy to clean.',
                'price_per_seat': Decimal('65.000'),
                'durability_rating': 4
            },
            {
                'name': 'Alcantara',
                'description': 'Premium synthetic suede-like material used in luxury vehicles. Soft touch with excellent durability.',
                'price_per_seat': Decimal('140.000'),
                'durability_rating': 5
            },
            {
                'name': 'Vinyl',
                'description': 'Water-resistant and easy to clean synthetic material. Great for high-traffic vehicles.',
                'price_per_seat': Decimal('45.000'),
                'durability_rating': 3
            },
            {
                'name': 'Nylon Fabric',
                'description': 'Durable synthetic fabric that resists wear and stains. Great for family vehicles.',
                'price_per_seat': Decimal('55.000'),
                'durability_rating': 4
            }
        ]

        for material_data in materials:
            UpholsteryMaterial.objects.get_or_create(
                name=material_data['name'],
                defaults={
                    'description': material_data['description'],
                    'price_per_seat': material_data['price_per_seat'],
                    'available': True,
                    'durability_rating': material_data['durability_rating']
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(materials)} upholstery materials'))

    def create_upholstery_types(self):
        """Create test upholstery service types"""
        upholstery_types = [
            {
                'name': 'Full Interior',
                'description': 'Complete upholstery service for the entire interior of your vehicle, including seats, door panels, headliner, and dashboard.',
                'base_price': Decimal('350.000'),
                'estimated_hours': 16
            },
            {
                'name': 'Seats Only',
                'description': 'Upholstery service for all seats in your vehicle, including front and back seats.',
                'base_price': Decimal('200.000'),
                'estimated_hours': 8
            },
            {
                'name': 'Front Seats Only',
                'description': 'Upholstery service for just the front seats of your vehicle.',
                'base_price': Decimal('120.000'),
                'estimated_hours': 4
            },
            {
                'name': 'Door Panels',
                'description': 'Upholstery service for all door panels in your vehicle.',
                'base_price': Decimal('100.000'),
                'estimated_hours': 6
            },
            {
                'name': 'Dashboard Cover',
                'description': 'Custom upholstery service for your vehicle\'s dashboard.',
                'base_price': Decimal('80.000'),
                'estimated_hours': 5
            }
        ]

        for type_data in upholstery_types:
            UpholsteryType.objects.get_or_create(
                name=type_data['name'],
                defaults={
                    'description': type_data['description'],
                    'base_price': type_data['base_price'],
                    'estimated_hours': type_data['estimated_hours'],
                    'available': True
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(upholstery_types)} upholstery service types'))

    def create_service_locations(self):
        """Create test service locations"""
        locations = [
            {
                'name': 'Main Showroom',
                'address': '123 Automotive Avenue, Manama, Bahrain',
                'phone': '+973 1234 5678',
                'email': 'mainshowroom@example.com',
                'working_hours_start': '09:00',
                'working_hours_end': '18:00'
            },
            {
                'name': 'Premium Service Center',
                'address': '456 Luxury Boulevard, Riffa, Bahrain',
                'phone': '+973 1234 9876',
                'email': 'premium@example.com',
                'working_hours_start': '10:00',
                'working_hours_end': '20:00'
            }
        ]

        for location_data in locations:
            ServiceLocation.objects.get_or_create(
                name=location_data['name'],
                defaults={
                    'address': location_data['address'],
                    'phone': location_data['phone'],
                    'email': location_data['email'],
                    'working_hours_start': location_data['working_hours_start'],
                    'working_hours_end': location_data['working_hours_end'],
                    'is_active': True
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(locations)} service locations'))

    def create_time_slots(self):
        """Create time slots for the next 7 days"""
        locations = ServiceLocation.objects.filter(is_active=True)
        if not locations.exists():
            self.stdout.write(self.style.WARNING('No active service locations found. Cannot create time slots.'))
            return

        # Delete existing future time slots to avoid duplicates
        today = timezone.now().date()
        ServiceTimeSlot.objects.filter(date__gte=today).delete()

        slots_created = 0

        # Create slots for the next 7 days
        for day_offset in range(1, 8):  # Starting from tomorrow
            slot_date = today + timedelta(days=day_offset)

            for location in locations:
                # Parse working hours
                start_hour = int(location.working_hours_start.hour)
                end_hour = int(location.working_hours_end.hour)

                # Create morning and afternoon slots
                morning_start = start_hour
                morning_end = min(start_hour + 3, end_hour - 1)

                afternoon_start = morning_end + 1
                afternoon_end = end_hour

                # Morning slot
                ServiceTimeSlot.objects.create(
                    location=location,
                    date=slot_date,
                    start_time=f"{morning_start:02d}:00:00",
                    end_time=f"{morning_end:02d}:00:00",
                    max_bookings=2 if location.name == 'Main Showroom' else 1,
                    current_bookings=0
                )
                slots_created += 1

                # Afternoon slot
                ServiceTimeSlot.objects.create(
                    location=location,
                    date=slot_date,
                    start_time=f"{afternoon_start:02d}:00:00",
                    end_time=f"{afternoon_end:02d}:00:00",
                    max_bookings=2 if location.name == 'Main Showroom' else 1,
                    current_bookings=0
                )
                slots_created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {slots_created} time slots for the next 7 days'))

    def create_sample_bookings(self):
        """Create sample bookings using existing vehicles"""
        # Get a few random vehicles

        # Get materials, types, and time slots
        materials = list(UpholsteryMaterial.objects.filter(available=True))
        upholstery_types = list(UpholsteryType.objects.filter(available=True))
        time_slots = list(ServiceTimeSlot.objects.filter(
            date__gte=timezone.now().date(),
            current_bookings__lt=2  # Ensure slot is available
        )[:10])

        if not materials or not upholstery_types or not time_slots:
            self.stdout.write(
                self.style.WARNING('Missing required data for bookings (materials, types, or time slots).'))
            return

        # Sample customer names and contact info
        customers = [
            {'name': 'Ahmed Al Khalifa', 'phone': '+973 3300 1122', 'email': 'ahmed@example.com'},
            {'name': 'Fatima Rahman', 'phone': '+973 3300 3344', 'email': 'fatima@example.com'},
            {'name': 'Mohammed Ali', 'phone': '+973 3300 5566', 'email': 'mohammed@example.com'},
            {'name': 'Sara Hussain', 'phone': '+973 3300 7788', 'email': 'sara@example.com'},
        ]

        # Statuses for variety
        statuses = [
            UpholsteryBooking.STATUS_PENDING,
            UpholsteryBooking.STATUS_CONFIRMED,
            UpholsteryBooking.STATUS_IN_PROGRESS,
            UpholsteryBooking.STATUS_COMPLETED
        ]

        # Create several bookings
        bookings_created = 0
        import random

        for i in range(3):
            customer = customers[i]
            primary_material = random.choice(materials)

            # Ensure accent material is different
            accent_options = [m for m in materials if m != primary_material]
            accent_material = random.choice(accent_options) if accent_options and random.choice([True, False]) else None

            upholstery_type = random.choice(upholstery_types)
            time_slot = time_slots[i % len(time_slots)]
            status = statuses[i % len(statuses)]

            # Calculate price
            base_price = upholstery_type.base_price
            seats = 4
            material_cost = primary_material.price_per_seat * seats

            total_price = base_price + material_cost

            if accent_material:
                accent_cost = accent_material.price_per_seat * seats * Decimal('0.3')
                total_price += accent_cost

            # Create booking
            booking = UpholsteryBooking.objects.create(
                upholstery_type=upholstery_type,
                primary_material=primary_material,
                accent_material=accent_material,
                time_slot=time_slot,
                user_id=1,
                status=status,
                total_price=total_price,
                deposit_paid=total_price * Decimal('0.2'),  # 20% deposit
                notes=f"Sample booking {primary_material.name} upholstery."
            )

            # Update slot booking count
            time_slot.current_bookings += 1
            time_slot.save()

            # Set completed date for completed bookings
            if status == UpholsteryBooking.STATUS_COMPLETED:
                booking.completed_at = timezone.now() - timedelta(days=random.randint(1, 5))
                booking.save()

            bookings_created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {bookings_created} sample bookings'))


if __name__ == '__main__':
    print("This script should be run as a Django management command.")
    print("Save it to your_app_name/management/commands/create_upholstery_data.py")
    print("Then run: python manage.py create_upholstery_data")
