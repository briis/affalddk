"""Tests for the affaldonline.dk PDF calendar parser.

Covers the real generated PDFs (Sorø, Fanø, Nyborg) and synthetic PDFs
built from ops, which pin the legend pairing, icon groups and the
missing-fraction warnings without another binary fixture.
"""
import datetime as dt
import zlib
from pathlib import Path

from custom_components.affalddk.pyaffalddk.affaldonline_pdf import parse_affaldonline_pdf

datadir = Path(__file__).parent / 'data'


def _pdf_from_ops(ops):
    """Wrap (kind, x, y, value) ops into a fake FlateDecode content stream."""
    lines = []
    for kind, x, y, value in ops:
        if kind == 'T':
            lines.append(f'q 0.000 g BT {x} {y} Td ({value}) Tj ET Q')
        else:
            lines.append(f'q 11.34 0 0 11.34 {x} {y} cm /{value} Do Q')
    content = '\n'.join(lines).encode('latin1')
    return (b'%PDF-1.4\n<< /Filter /FlateDecode /Length ' + str(len(content)).encode()
            + b' >>\nstream\n' + zlib.compress(content) + b'\nendstream\nendobj\n%%EOF\n')


def test_parse_affaldonline_pdf(capsys):
    with capsys.disabled():
        # Sorø Rådhus, Rådhusvej 8, 4180 Sorø
        pdf = (datadir / 'soroe_raadhus_2026.pdf').read_bytes()
        calendar = parse_affaldonline_pdf(pdf, 2026)
        assert len(calendar) == 91
        assert calendar[dt.date(2026, 1, 3)] == {'Plast/mad- og drikkekarton', 'Restaffald'}
        assert calendar[dt.date(2026, 1, 16)] == {'Glas', 'Metal', 'Plast/mad- og drikkekarton', 'Restaffald'}
        assert calendar[dt.date(2026, 1, 21)] == {'Storskrald'}
        assert calendar[dt.date(2026, 3, 18)] == {'Haveaffald'}
        assert calendar[dt.date(2026, 6, 12)] == {'Pap/papir', 'Plast/mad- og drikkekarton', 'Restaffald'}


def test_parse_affaldonline_pdf_fanoe(capsys):
    with capsys.disabled():
        # Fanø, Hovedgaden 1 A, 6720 Fanø
        pdf = (datadir / 'fanoe_hovedgaden_2026.pdf').read_bytes()
        calendar = parse_affaldonline_pdf(pdf, 2026)
        assert len(calendar) == 51
        assert calendar[dt.date(2026, 1, 2)] == {'Bioaffald', 'Restaffald'}
        assert calendar[dt.date(2026, 1, 6)] == {'Haveaffald'}
        assert calendar[dt.date(2026, 1, 15)] == {'Bioaffald', 'Restaffald'}
        assert calendar[dt.date(2026, 2, 17)] == {'Haveaffald'}


def test_parse_affaldonline_pdf_nyborg(capsys):
    with capsys.disabled():
        # Nyborg, Slotsgade 1 A, 5800 Nyborg
        pdf = (datadir / 'nyborg_slotsgade_2026.pdf').read_bytes()
        calendar = parse_affaldonline_pdf(pdf, 2026)
        assert len(calendar) == 33
        assert calendar[dt.date(2026, 1, 6)] == {'Haveaffald', 'Papir/Pap/Plast/Mad-drikkekarton', 'Restaffald'}
        assert calendar[dt.date(2026, 1, 20)] == {'Haveaffald', 'Restaffald'}
        assert calendar[dt.date(2026, 2, 3)] == {'Haveaffald', 'Papir/Pap/Plast/Mad-drikkekarton', 'Restaffald'}
        assert calendar[dt.date(2026, 3, 17)] == {'Haveaffald', 'Restaffald'}


def test_affaldonline_pdf_legend_pairing(capsys):
    """Legend icons pair with the nearest label to their right, in any op order."""
    ops = [
        ('T', 39.69, 186.64, 'JANUAR'),
        ('T', 39.69, 641.88, 'FRE'), ('T', 68.10, 641.88, '9'),
        ('I', 79.94, 640.63, 'I1'), ('I', 92.69, 640.63, 'I4'),
        ('T', 39.69, 627.71, 'MAN'), ('T', 62.50, 627.71, '12'),
        ('I', 79.94, 626.46, 'I9'),
        # Legend with the label emitted BEFORE its icons (the fragile order).
        ('T', 55.28, 172.46, 'Restaffald'),
        ('I', 39.69, 170.65, 'I1'),
        ('T', 141.41, 172.46, 'Pap'),
        ('I', 113.06, 170.65, 'I4'),
        ('T', 300.31, 172.46, 'Storskrald'),
        ('I', 271.96, 170.65, 'I9'),
    ]
    calendar = parse_affaldonline_pdf(_pdf_from_ops(ops), 2026)
    assert calendar == {dt.date(2026, 1, 9): {'Restaffald', 'Pap'},
                        dt.date(2026, 1, 12): {'Storskrald'}}
    assert capsys.readouterr().out == ''


def test_affaldonline_pdf_icon_groups(capsys):
    """Adjacent legend icons form a group; the same icon alone means less.

    Sorø case: the pap icon pairs with a partner icon for the combined
    Pap/papir fraction, and means plain Pap when drawn alone.
    """
    ops = [
        ('T', 39.69, 186.64, 'JANUAR'),
        ('T', 39.69, 641.88, 'FRE'), ('T', 68.10, 641.88, '9'),
        ('I', 79.94, 640.63, 'I4'), ('I', 92.69, 640.63, 'I5'),
        ('T', 39.69, 627.71, 'MAN'), ('T', 62.50, 627.71, '12'),
        ('I', 79.94, 626.46, 'I4'), ('I', 92.69, 626.46, 'I6'),
        # Legend: I4+I5 together -> Pap/papir, I4 alone -> Pap, I6 -> Glas.
        ('T', 271.96, 172.46, 'Pap/papir'),
        ('I', 246.44, 170.65, 'I4'), ('I', 259.20, 170.65, 'I5'),
        ('T', 371.60, 172.46, 'Pap'),
        ('I', 356.01, 170.65, 'I4'),
        ('T', 417.57, 172.46, 'Glas'),
        ('I', 401.98, 170.65, 'I6'),
    ]
    calendar = parse_affaldonline_pdf(_pdf_from_ops(ops), 2026)
    assert calendar == {
        dt.date(2026, 1, 9): {'Pap/papir'},
        dt.date(2026, 1, 12): {'Pap', 'Glas'},
    }
    assert capsys.readouterr().out == ''


def test_affaldonline_pdf_missing_icon_and_row(capsys):
    """Icons absent from the legend and date rows without fractions are reported."""
    ops = [
        ('T', 39.69, 186.64, 'JANUAR'),
        ('T', 39.69, 641.88, 'FRE'), ('T', 68.10, 641.88, '9'),
        ('I', 79.94, 640.63, 'I1'), ('I', 92.69, 640.63, 'I99'),
        ('T', 39.69, 627.71, 'MAN'), ('T', 62.50, 627.71, '12'),
        ('T', 39.69, 613.54, 'ONS'), ('T', 62.50, 613.54, '21'),
        ('I', 79.94, 612.28, 'I1'),
        # Legend defines only I1.
        ('T', 55.28, 172.46, 'Restaffald'),
        ('I', 39.69, 170.65, 'I1'),
    ]
    calendar = parse_affaldonline_pdf(_pdf_from_ops(ops), 2026)
    assert calendar == {dt.date(2026, 1, 9): {'Restaffald'},
                        dt.date(2026, 1, 21): {'Restaffald'}}
    assert capsys.readouterr().out == (
        "missing: icon I99 is not defined by the affaldonline legend\n"
        "missing: no fraction found for 2026-01-12 in the affaldonline PDF\n")
