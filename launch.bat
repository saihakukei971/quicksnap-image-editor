@echo off
echo QuickSnap ���N�����܂�...
python main.py
if %ERRORLEVEL% neq 0 (
    echo �G���[���������܂����B
    echo Python ���C���X�g�[������Ă��邱�Ƃ��m�F���Ă��������B
    echo �K�v�ȃp�b�P�[�W���C���X�g�[������ɂ�:
    echo   pip install -r requirements.txt
    pause
)