load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"

begin
  outdir = "outputs/figures"
  system("mkdir -p " + outdir)

  wks = gsn_open_wks("png", outdir + "/compare_plotchar_svg_runtime_ncl")

  txres = True
  txres@txFontHeightF = 0.036
  txres@txJust = "CenterLeft"
  txres@txFuncCode = "~"

  title = True
  title@txFontHeightF = 0.044
  title@txJust = "CenterLeft"
  title@txFuncCode = "~"

  gsn_text_ndc(wks, "NCL Plotchar reference", 0.08, 0.91, title)
  gsn_text_ndc(wks, "Plain: ABC abc 123", 0.08, 0.78, txres)
  gsn_text_ndc(wks, "Subscript: H~B~2~N~O", 0.08, 0.65, txres)
  gsn_text_ndc(wks, "Superscript: x~S~2~N~ + y~S~2~N~", 0.08, 0.52, txres)
  gsn_text_ndc(wks, "Move: A~H15~B~V10~C", 0.08, 0.39, txres)
  gsn_text_ndc(wks, "Zoom: A~X130~B~Y80~C~Z100~", 0.08, 0.26, txres)
  gsn_text_ndc(wks, "Carriage: Line1~C~Line2", 0.08, 0.13, txres)

  frame(wks)
end
