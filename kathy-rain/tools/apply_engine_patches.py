#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kathy Rain 汉化引擎补丁（AGS 3.6.3.15）

把中文字体回退、轮盘动作文字、撇号修正、Substring 越界保护等改动
应用到 AGS 3.6.3.15 源码树。

用法：
    python apply_engine_patches.py <AGS源码根目录>

示例：
    python apply_engine_patches.py D:/ags_src/ags_3.6.3.15_source

补丁只对 loaded_game_file_version < kGameVersion_350 生效，不影响新游戏。
"""

import sys
from pathlib import Path


def patch_file(path: Path, replacements, marker):
    text = path.read_text(encoding="utf-8")
    if marker in text:
        print(f"  skip (already patched): {path.name}")
        return
    for old, new in replacements:
        if old not in text:
            raise SystemExit(f"锚点未找到: {path}\n{old[:80]}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"  patched: {path.name}")


def main() -> None:
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(1)
    root = Path(sys.argv[1])
    if not (root / "Engine").is_dir():
        raise SystemExit("不是 AGS 源码根目录")

    print("1) 中文字体回退")
    fonts = root / "Common/font/fonts.cpp"
    helper = """
static bool has_high_bytes(const char *s)
{
    for (const unsigned char *p = (const unsigned char*)s; p && *p; ++p)
        if (*p >= 0x80) return true;
    return false;
}
"""
    fallback = """
    if (font_number != 19 && has_high_bytes(texx) && fonts.size() > 19 && fonts[19].Renderer)
        font_number = 19;"""
    patch_file(fonts, [
        ("int get_text_width(const char *texx, int font_number)",
         helper + "\nint get_text_width(const char *texx, int font_number)"),
        ("""int get_text_width(const char *texx, int font_number)
{
    if (!assert_font_renderer(font_number))
        return 0;""",
         """int get_text_width(const char *texx, int font_number)
{
    if (!assert_font_renderer(font_number))
        return 0;
""" + fallback),
        ("""void wouttextxy(Bitmap *ds, int x, int y, int font_number, color_t text_color, const char *texx)
{
    if (!assert_font_renderer(font_number))
        return;
""",
         """void wouttextxy(Bitmap *ds, int x, int y, int font_number, color_t text_color, const char *texx)
{
    if (!assert_font_renderer(font_number))
        return;
    if (font_number != 19 && has_high_bytes(texx) && fonts.size() > 19 && fonts[19].Renderer)
    {
        wouttextxy(ds, x, y, 19, text_color, texx);
        return;
    }
"""),
    ], "has_high_bytes")

    print("2) 老游戏 GUI 轮询")
    game_run = root / "Engine/main/game_run.cpp"
    patch_file(game_run, [
        ("""    int focused_gui = GetGUIAtDirect(mousex, mousey, kHit_Interactable);
    for (auto &gui : guis)
    {
        if (!gui.IsDisplayed()) continue; // not on screen
        if (!gui.IsClickable()) continue; // don't update non-clickable
        gui.Poll(mousex, mousey, focused_gui == gui.GetID());
    }""",
         """    const bool legacy = loaded_game_file_version < kGameVersion_350;
    int focused_gui = GetGUIAtDirect(mousex, mousey, kHit_Interactable);
    for (auto &gui : guis)
    {
        if (!gui.IsDisplayed()) continue; // not on screen
        if (!legacy && !gui.IsClickable()) continue;
        const bool focus = legacy ? gui.GetRect().IsInside(mousex, mousey) : (focused_gui == gui.GetID());
        gui.Poll(mousex, mousey, focus);
    }"""),
    ], "const bool legacy = loaded_game_file_version")

    print("3) 轮盘按钮悬停图形")
    button = root / "Engine/ac/button.cpp"
    patch_file(button, [
        ("""int Button_GetGraphic(GUIButton *butt) {
    // return currently displayed pic""",
         """int Button_GetGraphic(GUIButton *butt) {
    // legacy geometry hover: scripts compare Graphic with MouseOverGraphic
    if (loaded_game_file_version < kGameVersion_350)
    {
        const int mo = butt->GetMouseOverImage();
        if (mo > 0)
        {
            GUIMain *vc = nullptr;
            for (auto &g : guis) { if (g.GetID() == butt->GetParentID()) { vc = &g; break; } }
            if (vc && vc->IsDisplayed())
            {
                const int lx = mousex - vc->GetX();
                const int ly = mousey - vc->GetY();
                if (lx >= butt->GetX() && lx < butt->GetX() + butt->GetWidth() &&
                    ly >= butt->GetY() && ly < butt->GetY() + butt->GetHeight())
                    return mo;
            }
        }
    }
    // return currently displayed pic"""),
    ], "legacy geometry hover")

    print("4) 撇号修正（0xB3 / UTF-8 C2 B3 -> '）")
    label = root / "Engine/ac/label.cpp"
    patch_file(label, [
        ("void Label_SetText(GUILabel *labl, const char *newtx) {",
         """void Label_SetText(GUILabel *labl, const char *newtx) {
    if (newtx && strchr(newtx, (char)0xB3))
    {
        char fixed[8192];
        size_t n = 0;
        for (const char *p = newtx; *p && n + 1 < sizeof(fixed); ++p)
        {
            if ((unsigned char)p[0] == 0xC2 && (unsigned char)p[1] == 0xB3) { fixed[n++] = '\\''; ++p; }
            else if ((unsigned char)p[0] == 0xB3) { fixed[n++] = '\\''; }
            else { fixed[n++] = p[0]; }
        }
        fixed[n] = 0;
        labl->SetText(fixed);
        return;
    }"""),
    ], "strchr(newtx, (char)0xB3)")

    print("5) Substring 越界钳制")
    string_cpp = root / "Engine/ac/string.cpp"
    patch_file(string_cpp, [
        ("""const char* String_Substring(const char *thisString, int index, int length) {
    if (length < 0)
        quit("!String.Substring: invalid length");
    const auto &header = ScriptString::GetHeader(thisString);
    if ((index < 0) || ((size_t)index > header.ULength))
        quit("!String.Substring: invalid index");""",
         """const char* String_Substring(const char *thisString, int index, int length) {
    if (length < 0)
        length = 0;
    const auto &header = ScriptString::GetHeader(thisString);
    if (index < 0)
        index = 0;
    if ((size_t)index > header.ULength)
        index = (int)header.ULength;
    if (length == 0)
        return CreateNewScriptString("");"""),
    ], "length == 0)\n        return CreateNewScriptString")

    print("6) 视频模块空实现（无视频构建）")
    video = root / "Engine/media/video/video.cpp"
    if video.exists():
        text = video.read_text(encoding="utf-8")
        if "void video_single_pause()" not in text:
            text += "\nvoid video_single_pause() {}\nvoid video_single_resume() {}\n"
            video.write_text(text, encoding="utf-8")
            print("  patched: video.cpp")
        else:
            print("  skip (already patched): video.cpp")

    print("\n完成。")
    print("另外需要：")
    print("  - 编译器使用 /MT，并链接 dbghelp/psapi（按需）")
    print("  - 配置 AGS_NO_VIDEO_PLAYER=ON、SDLSOUND_DECODER_VORBIS=ON")
    print("  - 用 tools/pack_engine.py 正确合成 exe（避免 40 号房间黑屏）")


if __name__ == "__main__":
    main()
