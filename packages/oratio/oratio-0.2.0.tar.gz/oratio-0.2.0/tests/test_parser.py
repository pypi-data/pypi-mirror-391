"""
Test Parser
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from oratio.compiler.parser import SemanticParser
from oratio.compiler.errors import ParseError, ValidationError


def test_italian_simple():
    """Test parsing italiano semplice"""
    parser = SemanticParser()
    
    code = "Stampa 'Ciao Mondo!'"
    
    ir = parser.parse(code)
    
    assert 'version' in ir
    assert 'operations' in ir
    assert len(ir['operations']) > 0


def test_english_simple():
    """Test parsing inglese semplice"""
    parser = SemanticParser(language='en')
    
    code = "Print 'Hello World!'"
    
    ir = parser.parse(code)
    
    assert 'version' in ir
    assert 'operations' in ir
    assert len(ir['operations']) > 0


def test_language_detection():
    """Test rilevamento automatico lingua"""
    parser = SemanticParser()
    
    # Italiano
    code_it = "Carica il file vendite.csv"
    ir = parser.parse(code_it)
    assert ir is not None
    
    # Inglese
    code_en = "Load the file sales.csv"
    ir = parser.parse(code_en)
    assert ir is not None


def test_validation_error():
    """Test che IR invalido sollevi errore"""
    from oratio.compiler.validator import IRValidator
    
    validator = IRValidator()
    
    # IR senza version
    invalid_ir = {"operations": []}
    
    with pytest.raises(ValidationError):
        validator.validate(invalid_ir)


if __name__ == "__main__":
    print("🧪 Running tests...")
    
    print("\n1. Test italiano...")
    test_italian_simple()
    print("✅ OK")
    
    print("\n2. Test inglese...")
    test_english_simple()
    print("✅ OK")
    
    print("\n3. Test rilevamento lingua...")
    test_language_detection()
    print("✅ OK")
    
    print("\n4. Test validazione...")
    test_validation_error()
    print("✅ OK")
    
    print("\n🎉 Tutti i test passati!")
