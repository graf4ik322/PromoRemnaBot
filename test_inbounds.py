#!/usr/bin/env python3
"""
Test script to verify inbound UUIDs configuration
"""

import os
from config import Config

def test_inbound_configuration():
    """Test inbound configuration"""
    print("🧪 ТЕСТИРОВАНИЕ КОНФИГУРАЦИИ ИНБАУНДОВ")
    print("=" * 50)
    
    # Check current configuration
    current_inbounds = Config.DEFAULT_INBOUND_IDS
    print(f"📋 DEFAULT_INBOUND_IDS из config: {current_inbounds}")
    print(f"📝 Тип: {type(current_inbounds)}")
    print(f"🔢 Количество: {len(current_inbounds)}")
    
    # Check environment variable
    env_value = os.getenv('DEFAULT_INBOUND_IDS', '1')
    print(f"\n🌍 Переменная окружения DEFAULT_INBOUND_IDS: '{env_value}'")
    
    # Show what would be sent to API
    print(f"\n📤 Что будет отправлено в API:")
    print(f"   active_user_inbounds={current_inbounds}")
    
    # Check if these look like UUIDs or numeric IDs
    print(f"\n🔍 Анализ инбаундов:")
    for i, inbound in enumerate(current_inbounds):
        if isinstance(inbound, str) and len(inbound) >= 36:
            print(f"   {i+1}. '{inbound}' - выглядит как UUID ✅")
        elif isinstance(inbound, int):
            print(f"   {i+1}. {inbound} - числовой ID ⚠️")
        else:
            print(f"   {i+1}. '{inbound}' - неопределенный формат ❓")
    
    return current_inbounds

def show_before_after():
    """Show before/after comparison"""
    print("\n" + "=" * 50)
    print("📊 СРАВНЕНИЕ ДО/ПОСЛЕ")
    print("=" * 50)
    
    print("❌ БЫЛО:")
    print("   activate_all_inbounds=True")
    print("   ↳ Активировались ВСЕ инбаунды в системе")
    
    print(f"\n✅ СТАЛО:")
    print(f"   active_user_inbounds={Config.DEFAULT_INBOUND_IDS}")
    print("   ↳ Активируются ТОЛЬКО указанные в .env инбаунды")
    
    print(f"\n🎯 ПРЕИМУЩЕСТВА:")
    print("   - Контроль над конкретными инбаундами")
    print("   - Безопасность (не все инбаунды)")
    print("   - Настраиваемость через .env")

def show_env_examples():
    """Show environment variable examples"""
    print("\n" + "=" * 50)
    print("📝 ПРИМЕРЫ НАСТРОЙКИ .env")
    print("=" * 50)
    
    examples = [
        ("Один UUID", "DEFAULT_INBOUND_IDS=123e4567-e89b-12d3-a456-426614174000"),
        ("Несколько UUID", "DEFAULT_INBOUND_IDS=123e4567-e89b-12d3-a456-426614174000,987fcdeb-a123-45e6-f789-012345678901"),
        ("Смешанные ID", "DEFAULT_INBOUND_IDS=1,123e4567-e89b-12d3-a456-426614174000,2"),
        ("Только числовые", "DEFAULT_INBOUND_IDS=1,2,3")
    ]
    
    for name, example in examples:
        print(f"\n🔧 {name}:")
        print(f"   {example}")

if __name__ == "__main__":
    inbounds = test_inbound_configuration()
    show_before_after()
    show_env_examples()
    
    print("\n" + "🎯" * 25)
    print("РЕЗУЛЬТАТ:")
    print("✅ ИНБАУНДЫ: Теперь используются только из .env")
    print(f"📋 ТЕКУЩИЕ: {inbounds}")
    print("🔧 НАСТРОЙКА: Через переменную DEFAULT_INBOUND_IDS")
    print("🎯" * 25)