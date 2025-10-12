"""
String formatting utilities for BPML generator
Provides various case conversion functions for code generation
"""

import re


def dash_case(name):
    """Convert CamelCase to dash-case (kebab-case)
    Example: UserProfile -> user-profile
    """
    return re.sub(r'([a-zA-Z])(?=[A-Z])', r'\1-', name).lower()


def snake_case(name):
    """Convert CamelCase to snake_case
    Example: UserProfile -> user_profile
    """
    return re.sub(r'([a-zA-Z])(?=[A-Z])', r'\1_', name).lower()


def capitalize_str(name):
    """Capitalize first letter
    Example: user -> User
    """
    return name[0].upper() + name[1:] if name else name


def lower_first_str(name):
    """Lowercase first letter
    Example: User -> user
    """
    return name[0].lower() + name[1:] if name else name


def camel_case(name):
    """Convert snake_case or dash-case to camelCase
    Example: user_profile -> userProfile
    """
    components = re.split(r'[-_]', name)
    return components[0].lower() + ''.join(x.title() for x in components[1:])


def pascal_case(name):
    """Convert snake_case or dash-case to PascalCase
    Example: user_profile -> UserProfile
    """
    components = re.split(r'[-_]', name)
    return ''.join(x.title() for x in components)


def upper_case(name):
    """Convert to UPPER_CASE
    Example: userProfile -> USER_PROFILE
    """
    return re.sub(r'([a-zA-Z])(?=[A-Z])', r'\1_', name).upper()
