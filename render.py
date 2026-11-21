#!/usr/bin/env python3
"""Render the Levitron K3 catalogue image entirely offline."""
import io
import math
import os
from pathlib import Path

import cairosvg
from PIL import Image


def shadow(cx, cy, rx, ry, opacity=0.18):
    # Layered analytic falloff also works on SVG renderers without filter support.
    return ''.join(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx * (1-i*.025):.3f}" ry="{ry * (1-i*.025):.3f}" fill="#352c26" opacity="{opacity/23:.5f}"/>' for i in range(23))


def toast(x, y, angle, variant):
    outline = 'M -78,70 L -81,-23 C -107,-37 -101,-69 -74,-79 C -53,-100 -23,-96 0,-90 C 29,-103 63,-91 77,-75 C 104,-65 104,-34 82,-23 L 79,70 Q 0,83 -78,70 Z'
    inner = 'M -65,59 L -68,-30 C -90,-43 -87,-61 -66,-66 C -44,-84 -23,-81 0,-76 C 25,-89 53,-78 65,-63 C 86,-58 88,-43 69,-31 L 66,59 Q 0,69 -65,59 Z'
    parts = [f'<g transform="translate({x} {y}) rotate({angle})">', f'<path d="{outline}" fill="#6b3015" transform="translate(5 5)"/>', f'<path d="{outline}" fill="url(#crust)" stroke="#9c501c" stroke-width="1.2"/>', f'<path d="{inner}" fill="url(#crumb)" stroke="#f3cc78" stroke-width="2"/>']
    for i in range(240):
        px = -63 + ((i * 47 + variant * 17) % 127)
        py = -59 + ((i * 71 + variant * 29) % 116)
        if py < -46 and abs(px) > 49:
            continue
        r = .65 + ((i * 19) % 15) / 10
        parts.append(f'<ellipse cx="{px}" cy="{py}" rx="{r:.2f}" ry="{r*.68:.2f}" fill="{["#9a511e", "#fff0b1", "#ba722b", "#e7ad51"][i%4]}" opacity="{.17+(i%5)*.055:.3f}"/>')
    for i in range(14):
        px = -54 + (i*31+variant*7)%108
        py = -44 + (i*43)%96
        parts.append(f'<path d="M {px} {py} q 3 -3 6 0 q -2 5 -6 0" fill="#a76628" opacity=".22"/><path d="M {px} {py+2} q 3 3 6 0" fill="none" stroke="#fff2bd" stroke-width=".7" opacity=".55"/>')
    parts.append(f'<path d="M -77 63 L -79 -25 C -103 -40 -96 -67 -74 -74" fill="none" stroke="#f5be64" stroke-width="2" opacity=".75"/></g>')
    return ''.join(parts)


def make_svg():
    s = ['''<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="2048" viewBox="0 0 2048 2048">
<defs>
 <linearGradient id="background" x2="0" y2="1"><stop stop-color="#eeeae2"/><stop offset=".57" stop-color="#f6f3ed"/><stop offset="1" stop-color="#d8d5ce"/></linearGradient>
 <radialGradient id="vignette"><stop offset=".32" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#70675c" stop-opacity=".15"/></radialGradient>
 <linearGradient id="counter" x2="0" y2="1"><stop stop-color="#eeece6" stop-opacity="0"/><stop offset=".3" stop-color="#e9e6df"/><stop offset=".7" stop-color="#e4e0d8"/><stop offset="1" stop-color="#d5d0c7"/></linearGradient>
 <linearGradient id="chrome" x1="0" y1="0" x2="1" y2=".13"><stop stop-color="#8c9392"/><stop offset=".04" stop-color="#d4d8d5"/><stop offset=".12" stop-color="#f3f4ef"/><stop offset=".32" stop-color="#dadcd7"/><stop offset=".52" stop-color="#b1b7b3"/><stop offset=".66" stop-color="#e8eae5"/><stop offset=".83" stop-color="#c0c5c0"/><stop offset="1" stop-color="#858e8a"/></linearGradient>
 <linearGradient id="frontShade" x2="0" y2="1"><stop stop-color="#fff" stop-opacity=".25"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/><stop offset=".8" stop-color="#343e39" stop-opacity=".05"/><stop offset="1" stop-color="#313c36" stop-opacity=".38"/></linearGradient>
 <linearGradient id="top" x1=".1" y1="0" x2=".65" y2="1"><stop stop-color="#f8f8f1"/><stop offset=".25" stop-color="#d3d8d2"/><stop offset=".52" stop-color="#a1aaa4"/><stop offset=".73" stop-color="#edf0e9"/><stop offset="1" stop-color="#a9b0a9"/></linearGradient>
 <linearGradient id="side" x2="1" y2=".3"><stop stop-color="#959c94"/><stop offset=".2" stop-color="#d2d5ca"/><stop offset=".65" stop-color="#939a90"/><stop offset="1" stop-color="#626c62"/></linearGradient>
 <linearGradient id="enamel" x2="1" y2=".6"><stop stop-color="#f4ecd8"/><stop offset=".44" stop-color="#e4d9bd"/><stop offset="1" stop-color="#b3ab94"/></linearGradient>
 <linearGradient id="crust" x2=".8" y2="1"><stop stop-color="#e7b257"/><stop offset=".3" stop-color="#ba6c25"/><stop offset=".75" stop-color="#95501c"/><stop offset="1" stop-color="#6d3519"/></linearGradient>
 <radialGradient id="crumb" cx=".41" cy=".35" r=".8"><stop stop-color="#f9d586"/><stop offset=".4" stop-color="#ebba60"/><stop offset=".74" stop-color="#d28b37"/><stop offset="1" stop-color="#a86423"/></radialGradient>
 <linearGradient id="ceramic" x2="0" y2="1"><stop stop-color="#fffefa"/><stop offset=".5" stop-color="#f6f5ef"/><stop offset="1" stop-color="#b9bcb7"/></linearGradient>
 <linearGradient id="butter" x2=".6" y2="1"><stop stop-color="#fff1ad"/><stop offset=".4" stop-color="#f7d572"/><stop offset="1" stop-color="#c69d3d"/></linearGradient>
 <linearGradient id="knife" x2=".25" y2="1"><stop stop-color="#fcffff"/><stop offset=".3" stop-color="#b7bfba"/><stop offset=".49" stop-color="#f8faf4"/><stop offset=".6" stop-color="#838f89"/><stop offset="1" stop-color="#cbd0c9"/></linearGradient>
 <filter id="soft"><feGaussianBlur stdDeviation="7"/></filter>
 <filter id="glow"><feGaussianBlur stdDeviation="4"/></filter>
 <filter id="specular"><feGaussianBlur stdDeviation="3"/></filter>
 <clipPath id="frontClip"><path d="M225 524 Q224 503 250 505 L651 526 Q679 528 680 557 L680 749 Q680 780 650 784 L253 770 Q226 768 225 740Z"/></clipPath>
</defs>
<g transform="scale(2)">
<path fill="url(#background)" d="M0 0H1024V1024H0Z"/>
<path fill="url(#counter)" d="M0 545H1024V1024H0Z"/>
<path fill="url(#vignette)" d="M0 0H1024V1024H0Z"/>
''']
    s += [shadow(507, 787, 312, 40, .19), shadow(470, 787, 246, 21, .30), shadow(820, 802, 111, 15, .18)]
    # Faint broad reflections on the matte studio counter.
    s.append('<path d="M254 795 L645 809 L668 849 L261 833Z" fill="#a4aaa0" opacity=".045"/>')
    s.append('''<path d="M268 758 L308 760 L308 788 Q287 796 268 784Z" fill="#41463f"/>
<path d="M631 768 L665 763 L665 791 Q648 799 632 790Z" fill="#333a33"/>
<path d="M733 697 L759 686 L758 719 L735 731Z" fill="#40463d"/>
<path d="M650 525 L772 454 Q789 454 790 479 L789 683 Q790 708 770 721 L677 775Z" fill="url(#side)" stroke="#7f887e" stroke-width="1.5"/>
<path d="M699 549 L766 507 Q776 501 776 517 L776 670 Q776 687 764 695 L699 736 Q689 742 689 727 L689 567 Q689 556 699 549Z" fill="url(#enamel)" stroke="#7e877b" stroke-width="2"/>
<path d="M697 568 L697 720" stroke="#fff9e7" stroke-width="2" opacity=".65"/>
<path d="M225 524 Q224 503 250 505 L651 526 Q679 528 680 557 L680 749 Q680 780 650 784 L253 770 Q226 768 225 740Z" fill="url(#chrome)" stroke="#939b94" stroke-width="1.5"/>
<path d="M225 524 Q224 503 250 505 L651 526 Q679 528 680 557 L680 749 Q680 780 650 784 L253 770 Q226 768 225 740Z" fill="url(#frontShade)"/>
''')
    # Hundreds of fine brushed-metal machining lines, clipped to the housing.
    s.append('<g clip-path="url(#frontClip)">')
    for i in range(172):
        yy = 516 + i*1.57
        s.append(f'<path d="M229 {yy:.2f} L679 {yy+15:.2f}" stroke="{"#ffffff" if i%3 else "#64736b"}" stroke-width=".45" opacity="{.055+(i%4)*.014:.3f}"/>')
    s.append('''<rect x="256" y="539" width="21" height="200" rx="10" fill="white" opacity=".35" filter="url(#specular)" transform="rotate(1 256 539)"/>
<path d="M284 535L300 536L301 750L286 749Z" fill="white" opacity=".13"/>
</g>
<path d="M229 518 Q228 505 245 496 L350 433 Q365 424 385 426 L764 448 Q783 448 785 462 L680 531 Q668 541 647 539 L247 518Z" fill="url(#top)" stroke="#a5ada5" stroke-width="1.5"/>
<path d="M239 512 L649 535 Q665 538 679 529 L779 465" stroke="#fcfff6" stroke-width="2" fill="none" opacity=".85"/>
<g transform="translate(365 477) rotate(-10)">
<rect x="-96" y="-14" width="192" height="28" rx="12" fill="#f1f2e9"/>
<rect x="-92" y="-11" width="184" height="23" rx="10" fill="#626a60"/>
<rect x="-88" y="-8" width="176" height="17" rx="7" fill="#20261f"/>
<path d="M-80 5H79" stroke="#ab7948" stroke-width="2" opacity=".5"/>
</g>
<g transform="translate(584 477) rotate(-10)">
<rect x="-96" y="-14" width="192" height="28" rx="12" fill="#f1f2e9"/>
<rect x="-92" y="-11" width="184" height="23" rx="10" fill="#626a60"/>
<rect x="-88" y="-8" width="176" height="17" rx="7" fill="#20261f"/>
<path d="M-80 5H79" stroke="#ab7948" stroke-width="2" opacity=".5"/>
</g>
<path d="M238 744 L650 758 Q665 758 671 751" stroke="#5f6b61" stroke-width="1" fill="none" opacity=".65"/>
<path d="M239 747 L650 761" stroke="#f3f4ec" stroke-width="1.2" opacity=".65"/>
<g transform="translate(392 659) rotate(2)">
<rect x="0" y="0" width="133" height="30" rx="4" fill="#747f74" opacity=".6"/>
<rect x="1" y="-1" width="131" height="28" rx="4" fill="#d7dbd2" stroke="#f6f7f0" stroke-width=".8"/>
<text x="67" y="17" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="600" letter-spacing="2" fill="#5f6a60">LEVITRON K3</text>
<circle cx="7" cy="12" r="1.5" fill="#8a9489"/><circle cx="126" cy="12" r="1.5" fill="#8a9489"/>
</g>
<path d="M730 549 L730 610" stroke="#7b816f" stroke-width="8" stroke-linecap="round"/>
<path d="M729 551 L729 606" stroke="#39463c" stroke-width="3" stroke-linecap="round"/>
<path d="M717 576 L741 561 Q746 558 750 565 L753 572 Q755 577 748 581 L724 594 Q717 594 714 587 Q711 581 717 576Z" fill="url(#knife)" stroke="#8c9588"/>
<ellipse cx="731" cy="654" rx="14" ry="19" transform="rotate(25 731 654)" fill="#7f8879"/>
<ellipse cx="730" cy="652" rx="12" ry="17" transform="rotate(25 730 652)" fill="url(#knife)" stroke="#c9cec0"/>
<path d="M729 640L733 644" stroke="#4d5c4c" stroke-width="1.4"/>
''')
    # The two hovering slices cast separate shadows on the counter.
    s += [shadow(357, 805, 85, 13, .055), shadow(565, 814, 81, 12, .05)]
    for x, y, angle in [(360, 402, -8), (579, 388, 9)]:
        s.append(f'<g transform="translate({x} {y}) rotate({angle})" fill="none">')
        for rx, ry, op, width in [(102, 19, .055, 10), (98, 17, .12, 2), (108, 23, .06, 1.1)]:
            s.append(f'<ellipse rx="{rx}" ry="{ry}" stroke="#e9a242" stroke-width="{width}" opacity="{op}" filter="url(#glow)"/>')
        s.append('</g>')
    s += [toast(357, 335, -8, 0), toast(579, 317, 8, 1)]
    # Single accessory: a porcelain butter dish, with one curled shaving and knife.
    s.append('''<path d="M728 780 Q726 769 742 762 L866 752 Q883 752 900 768 L916 786 Q921 795 906 801 L774 816 Q756 817 747 806Z" fill="url(#ceramic)" stroke="#bcc0b8" stroke-width="1"/>
<path d="M729 779 Q727 771 744 766 L866 756 Q883 755 895 771 L910 786 Q913 792 901 794 L773 809 Q760 810 751 800Z" fill="#fffefa" stroke="#e8e9e1" stroke-width="1.8"/>
<path d="M749 778 Q747 774 760 771 L859 763 Q870 762 878 771 L890 784 L770 798Z" fill="#eeeee6" stroke="#d7d9d0" stroke-width=".9"/>
<path d="M791 782 Q808 789 840 780" stroke="#94805a" stroke-width="5" opacity=".13" stroke-linecap="round"/>
<path d="M787 780 C777 764 788 745 807 742 C827 738 843 749 839 764 C836 774 824 779 813 773 C804 768 806 757 817 756 C824 755 828 760 825 764 C836 760 826 745 811 749 C798 752 794 763 802 775 L819 781 Q803 787 787 780Z" fill="url(#butter)" stroke="#dbb45d" stroke-width=".7"/>
<path d="M790 774 C785 756 800 744 812 745 C825 744 837 753 835 762" fill="none" stroke="#fff4bf" stroke-width="3"/>
<path d="M812 774 C804 766 807 757 817 756 C824 755 828 760 825 764" fill="none" stroke="#b38c36" stroke-width="1.3"/>
<path d="M794 799 L884 769" stroke="#646b62" stroke-width="7" stroke-linecap="round" opacity=".12"/>
<path d="M783 802 C776 803 773 797 780 794 L843 775 C852 769 867 760 881 761 Q889 762 883 769 C873 779 859 783 848 783 L786 803Z" fill="url(#knife)" stroke="#a1aaa0" stroke-width=".7"/>
<path d="M782 796 L842 778 Q863 764 881 763" fill="none" stroke="#fff" stroke-width="1.4" opacity=".85"/>
<path d="M845 777L848 783" stroke="#738174" stroke-width=".7"/>
</g></svg>''')
    return ''.join(s)


def render(svg):
    source = cairosvg.svg2png(bytestring=svg.encode('utf-8'), output_width=2048, output_height=2048)
    image = Image.open(io.BytesIO(source)).convert('RGB').resize((1024, 1024), Image.Resampling.LANCZOS)
    output = io.BytesIO()
    image.save(output, format='PNG', optimize=True)
    data = output.getvalue()
    if len(data) > 1048576:
        # Keep a true RGB PNG; deterministic fine colour quantization bounds size.
        image = image.quantize(colors=256, method=Image.Quantize.MEDIANCUT).convert('RGB')
        output = io.BytesIO()
        image.save(output, format='PNG', optimize=True)
        data = output.getvalue()
    assert len(data) <= 1048576, 'PNG exceeds 1 MiB'
    check = Image.open(io.BytesIO(data))
    assert check.size == (1024, 1024) and check.mode == 'RGB'
    return data


def main():
    svg = make_svg()
    data = render(svg)
    assert data == render(svg), 'Rendering must be byte-identical'
    destination = Path(os.environ.get('MAKEFUN_OUTPUT_DIR', '.'))
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'entry.png').write_bytes(data)
    print(f'Rendered entry.png: 1024x1024 RGB; {len(data)} bytes')


if __name__ == '__main__':
    main()
