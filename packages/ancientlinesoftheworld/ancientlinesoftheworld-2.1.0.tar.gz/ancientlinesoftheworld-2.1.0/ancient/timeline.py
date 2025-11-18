from datetime import datetime
from .mappings import (
    convert_to_cuneiform,
    convert_to_pahlavi,
    convert_to_manichaean,
    convert_to_hieroglyph,
    convert_to_akkadian,
    convert_to_oracle_bone,
    convert_to_avestan,
    
)



class AncientTimeline:
    
    """
    نمایش تایم‌لاین (زمان کنونی) با خطوط باستانی مختلف
    نویسنده: امیرحسین خزاعی
    """

    def __init__(self, script: str = 'cuneiform'):
        """
        
        Args:
            script (str): انتخاب زبان باستانی (cuneiform, pahlavi, manichaean, hieroglyph, akkadian, oracle_bone)
        """
        supported_scripts = [
            'cuneiform', 'pahlavi', 'manichaean',
            'hieroglyph', 'akkadian', 'oracle_bone','avestan'
        ]
        if script not in supported_scripts:
            raise ValueError(f"❌ زبان نامعتبر است. گزینه‌های معتبر: {supported_scripts}")

        self.script = script

    def _convert_text(self, text: str) -> str:
        """تبدیل متن به زبان باستانی انتخابی"""
        if self.script == 'cuneiform':
            return convert_to_cuneiform(text)
        elif self.script == 'pahlavi':
            return convert_to_pahlavi(text)
        elif self.script == 'manichaean':
            return convert_to_manichaean(text)
        elif self.script == 'hieroglyph':
            return convert_to_hieroglyph(text)
        elif self.script == 'akkadian':
            return convert_to_akkadian(text)
        elif self.script == 'oracle_bone':
            return convert_to_oracle_bone(text)
        elif self.script == "avestan":
            return convert_to_avestan(text)
        
            
        return text
    

    def get_ancient_time(self) -> str:
        """گرفتن زمان فعلی به زبان باستانی"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        return self._convert_text(date_str)

    def show(self):
        
        print("📜 Ancient Timeline:")
        print("   ", self.get_ancient_time())