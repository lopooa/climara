load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"

begin
  outdir = "outputs/figures"
  system("mkdir -p " + outdir)

  wks = gsn_open_wks("png", outdir + "/ncl_plotchar_text_compare")

  txres = True
  txres@txFontHeightF = 0.032
  txres@txJust = "CenterCenter"
  txres@txFuncCode = "~"

  small = True
  small@txFontHeightF = 0.014
  small@txJust = "CenterLeft"

  title = True
  title@txFontHeightF = 0.022
  title@txJust = "CenterCenter"

  gsn_text_ndc(wks, "NCL Plotchar / Text diagnostic PNG", 0.50, 0.965, title)
  gsn_text_ndc(wks, "Compare with outputs/figures/python_plotchar_text_compare.svg", 0.50, 0.935, small)

  labels = (/"Plain",              "Subscript B/N",              "Superscript S/N",              "Script B/S/E/N",              "Font switch F22/F21",              "Case U/L",              "Carriage C",              "Movement H/V",              "Zoom X/Y/Z"/)

  strings = (/"ABC abc 123",               "H~B~2~N~O",               "x~S~2~N~ + y~S~2~N~",               "A~B~sub~E~B~sub2~N~  B~S~sup~E~S~sup2~N~",               "Font21 ~F22~Font22 ~F21~Font21",               "~U~abc DEF~L~ ABC def~N~",               "Line1~C~Line2",               "A~H15~B~V10~C",               "A~X130~B~Y80~C~Z100~"/)

  y0 = 0.86
  dy = 0.085

  do i = 0, dimsizes(strings)-1
    y = y0 - i * dy
    gsn_text_ndc(wks, labels(i), 0.08, y, small)
    gsn_text_ndc(wks, strings(i), 0.50, y, txres)

    plres = True
    plres@gsLineColor = "gray60"
    plres@gsLineThicknessF = 1.0
    gsn_polyline_ndc(wks, (/0.28,0.72/), (/y,y/), plres)
  end do

  frame(wks)
end
