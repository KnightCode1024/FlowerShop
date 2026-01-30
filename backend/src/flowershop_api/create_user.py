import sys
import asyncio
import getpass
import argparse
import os

from flowershop_api.services import UserService
from flowershop_api.schemas.user import UserCreateConsole
from flowershop_api.models import RoleEnum
from flowershop_api.entrypoint.ioc.integrations.console_integration import (
    inject,
)
from flowershop_api.entrypoint.setup import create_async_container
from flowershop_api.entrypoint.ioc.registry import get_providers

from dishka import FromDishka

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")


@inject
async def create_user_from_args(
    args,
    dishka_container,
    user_service: FromDishka[UserService],
):
    email = get_email(args)
    username = get_username(args)
    role = get_role(args)
    password = get_password(args)

    user_data = UserCreateConsole(
        email=email,
        username=username,
        role=role,
        password=password,
    )
    try:
        result = await user_service.create_user_for_console(user_data)
        print("----------------------------------------")
        print("| User created successfully!           |")
        print("----------------------------------------")
        print(f"| ID:       {result.id:<27} |")
        print("----------------------------------------")
        print(f"| Email:    {result.email:<27} |")
        print("----------------------------------------")
        print(f"| Username: {result.username:<27} |")
        print("----------------------------------------")
        print(f"| Role:     {result.role:<27} |")
        print("----------------------------------------")
        return result
    except Exception as e:
        print(f"Error creating user: {e}")
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create a new user",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--email",
        type=str,
        help="User email address",
    )
    parser.add_argument("--username", type=str, help="Username")
    parser.add_argument(
        "--role",
        type=str,
        help="User role: 1=user, 2=employee, 3=admin (default: 1)",
    )
    parser.add_argument(
        "--password",
        type=str,
        help="User password",
    )
    return parser.parse_args()


def get_user_input(
    prompt: str,
    default: str = None,
    hide_input: bool = False,
) -> str:
    if default:
        prompt = f"{prompt} (default: {default}): "
    else:
        prompt = f"{prompt}: "

    if hide_input:
        value = getpass.getpass(prompt)
    else:
        value = input(prompt).strip()
        if isinstance(value, str):
            value = value.encode("utf-8").decode("utf-8")

    return value if value else (default or "")


def get_email(args):
    if args.email:
        return args.email
    email = get_user_input("Email")
    if not email:
        print("Error: Email is required")
        sys.exit(1)
    return email


def get_username(args):
    if args.username:
        return args.username
    username = get_user_input("Username")
    if not username:
        print("Error: Username is required")
        sys.exit(1)
    return username


def get_role(args):
    if args.role:
        role_input = args.role.lower()
        if role_input == "1" or role_input == "user":
            return RoleEnum.USER
        elif role_input == "2" or role_input == "employee":
            return RoleEnum.EMPLOYEE
        elif role_input == "3" or role_input == "admin":
            return RoleEnum.ADMIN
        else:
            print(
                f"Error: Invalid role '{args.role}'.",
                "Use 1, 2, 3 or user, employee, admin.",
            )
            sys.exit(1)

    print("\nAvailable roles:")
    print("1. user (8+ chars, 1 uppercase, 1 digit)")
    print("2. employee (12+ chars, 1 uppercase, 1 digit, 1 special char)")
    print("3. admin (12+ chars, 1 uppercase, 1 digit, 1 special char)")

    while True:
        role_input = get_user_input("Choose role (1-3)", "1")
        if not role_input:
            role_input = "1"

        if role_input == "1":
            return RoleEnum.USER
        elif role_input == "2":
            return RoleEnum.EMPLOYEE
        elif role_input == "3":
            return RoleEnum.ADMIN
        else:
            print("Error: Please enter 1, 2, or 3.")


def get_password(args):
    if args.password:
        return args.password

    while True:
        password = get_user_input("Password", hide_input=True)
        if not password:
            print("Error: Password is required")
            continue

        password_confirm = get_user_input("Password (again)", hide_input=True)
        if password != password_confirm:
            print("Error: Passwords don't match. Please try again.")
            continue

        break

    return password


async def main():
    try:
        args = parse_args()
        container = create_async_container(get_providers())
        await create_user_from_args(args, dishka_container=container)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
