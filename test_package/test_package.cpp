#include <iostream>
#include <ass.h>

char testass[] = R"EOF([Script Info]
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,测试Foobarfoobar
)EOF";

int main()
{
    ASS_Library *libr = ass_library_init();
    ASS_Renderer *rend = ass_renderer_init(libr);
    ass_set_frame_size(rend, 1280, 720);

    ASS_Track *tck = ass_read_memory(libr, testass, sizeof(testass), "utf-8");
    int chg = 0;
    ASS_Image * img = ass_render_frame(rend, tck, 0L, &chg);

    ass_free_track(tck);
    ass_renderer_done(rend);
    ass_library_done(libr);
    return 0;
}
