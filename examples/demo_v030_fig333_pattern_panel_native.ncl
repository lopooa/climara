load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"

undef("make_pattern")
function make_pattern(lat[*]:numeric, lon[*]:numeric, mode:string, scale:numeric)
local nlat, nlon, lon2d, lat2d, deg2rad, data, active
begin
  nlat = dimsizes(lat)
  nlon = dimsizes(lon)

  deg2rad = 0.017453292519943295

  lon2d = conform_dims((/nlat, nlon/), lon, 1)
  lat2d = conform_dims((/nlat, nlon/), lat, 0)

  if (mode .eq. "sam") then
    data = -1.2 * cos((lat2d + 55.0) * deg2rad) \
           + 0.8 * sin((2.0 * lon2d) * deg2rad)
    active = lat2d .le. -20.0
  else
    if (mode .eq. "nao") then
      data = 1.4 * cos((lat2d - 55.0) * deg2rad) \
             - 0.9 * cos((2.0 * lon2d) * deg2rad)
      active = lat2d .ge. 20.0
    else
      data = 1.3 * cos((lat2d - 70.0) * deg2rad) \
             + 0.8 * sin(lon2d * deg2rad)
      active = lat2d .ge. 20.0
    end if
  end if

  data = data * scale
  data@_FillValue = -9999.0
  data = where(active, data, data@_FillValue)

  data!0 = "lat"
  data!1 = "lon"
  data&lat = lat
  data&lon = lon

  return(data)
end


begin
  system("mkdir -p outputs/figures")

  nlat = 73
  nlon = 144

  lat = fspan(-90.0, 90.0, nlat)
  lon = fspan(0.0, 357.5, nlon)

  nam_obs = make_pattern(lat, lon, "nam", 2.6)
  nao_obs = make_pattern(lat, lon, "nao", 2.6)
  sam_obs = make_pattern(lat, lon, "sam", 2.3)

  nam_mme = make_pattern(lat, lon, "nam", 2.2)
  nao_mme = make_pattern(lat, lon, "nao", 2.1)
  sam_mme = make_pattern(lat, lon, "sam", 2.0)

  wks = gsn_open_wks("png", "outputs/figures/v030_fig333_pattern_panel_native_ncl")

  plot = new(6, graphic)

  res = True
  res@gsnDraw = False
  res@gsnFrame = False

  res@cnFillOn = True
  res@cnLinesOn = False
  res@cnLineLabelsOn = False
  res@cnLevelSelectionMode = "ExplicitLevels"
  res@cnLevels = (/-5., -4., -3., -2., -1., 0., 1., 2., 3., 4., 5./)
  res@cnFillPalette = "BlueWhiteOrangeRed"
  res@cnFillDrawOrder = "PreDraw"

  res@lbLabelBarOn = False
  res@lbOrientation = "horizontal"
  res@lbBoxLineColor = "gray70"
  res@lbLabelFontHeightF = 0.010
  res@lbBoxEndCapStyle = "TriangleBothEnds"
  res@lbTitleOn = True
  res@lbTitleString = "(hPa)"
  res@lbTitlePosition = "Bottom"
  res@lbTitleFontHeightF = 0.010

  res@mpProjection = "Stereographic"
  res@mpCenterLonF = 0.0
  res@mpFillOn = False
  res@mpOutlineOn = True
  res@mpGridAndLimbOn = False
  res@mpPerimOn = True
  res@mpGeophysicalLineColor = "gray42"
  res@mpGeophysicalLineThicknessF = 2.0
  res@mpOutlineDrawOrder = "Draw"
  res@mpPerimDrawOrder = "PostDraw"

  res@gsnPolarLabelFontHeightF = 0.0
  res@gsnRightString = ""
  res@gsnLeftString = ""
  res@gsnCenterStringFontHeightF = 0.022

  nhres = res
  nhres@gsnPolar = "NH"
  nhres@mpMinLatF = 20.0
  nhres@mpCenterLatF = 90.0

  shres = res
  shres@gsnPolar = "SH"
  shres@mpMaxLatF = -20.0
  shres@mpCenterLatF = -90.0

  nhres@gsnCenterString = "NAM obs"
  plot(0) = gsn_csm_contour_map_polar(wks, nam_obs, nhres)

  nhres@gsnCenterString = "NAO obs"
  plot(1) = gsn_csm_contour_map_polar(wks, nao_obs, nhres)

  shres@gsnCenterString = "SAM obs"
  plot(2) = gsn_csm_contour_map_polar(wks, sam_obs, shres)

  nhres@gsnCenterString = "NAM historical MME"
  plot(3) = gsn_csm_contour_map_polar(wks, nam_mme, nhres)

  nhres@gsnCenterString = "NAO historical MME"
  plot(4) = gsn_csm_contour_map_polar(wks, nao_mme, nhres)

  shres@gsnCenterString = "SAM historical MME"
  plot(5) = gsn_csm_contour_map_polar(wks, sam_mme, shres)

  nao_box_lon = (/-90., 40., 40., -90., -90./)
  nao_box_lat = (/ 20., 20., 80.,  80.,  20./)

  boxres = True
  boxres@gsLineColor = "black"
  boxres@gsLineThicknessF = 1.5

  dum = new(2, graphic)
  dum(0) = gsn_add_polyline(wks, plot(1), nao_box_lon, nao_box_lat, boxres)
  dum(1) = gsn_add_polyline(wks, plot(4), nao_box_lon, nao_box_lat, boxres)

  panres = True
  panres@gsnFrame = False
  panres@gsnDraw = True

  panres@gsnPanelTop = 0.94
  panres@gsnPanelBottom = 0.43
  panres@gsnPanelLabelBar = True
  panres@gsnPanelYWhiteSpacePercent = 3.0
  panres@gsnPanelXWhiteSpacePercent = 3.0
  panres@gsnPanelDebug = True

  panres@pmLabelBarHeightF = 0.05
  panres@pmLabelBarWidthF = 0.38
  panres@pmLabelBarOrthogonalPosF = 0.005

  panres@lbLabelFontHeightF = 0.010
  panres@lbBoxLineColor = "gray70"
  panres@lbBoxEndCapStyle = "TriangleBothEnds"
  panres@lbTitleOn = True
  panres@lbTitleString = "(hPa)"
  panres@lbTitlePosition = "Bottom"
  panres@lbTitleFontHeightF = 0.010

  gsn_panel(wks, plot, (/2, 3/), panres)


  ; Source-style spatial-pattern legend blocks.
  ; Extracted from the original NCL script logic.
  tlres = True
  tlres@txFontHeightF = 0.008
  tlres@txJust = "CenterLeft"

  res_marker = True
  res_marker@gsMarkerIndex = 5
  res_marker@gsMarkerSizeF = 0.002
  res_marker@gsMarkerThicknessF = 0.5
  res_marker@gsMarkerOpacityF = 0.6

  pmres0 = True
  pmres0@gsFillColor = "gray25"
  pmres0@gsFillScaleF = 0.7
  pmres0@gsFillIndex = 3

  lres = True
  lres@gsLineDashPattern = 0
  lres@gsLineThicknessF = 1.0

  ; Right-side legend: < 80% of runs agree on sign
  x1 = 0.695
  x2 = 0.715
  y1 = 0.47
  y2 = 0.49

  gsn_polygon_ndc(wks, (/x1, x2, x2, x1/), (/y1, y1, y2, y2/), pmres0)
  gsn_polyline_ndc(wks, (/x1, x2, x2, x1, x1/), (/y1, y1, y2, y2, y1/), lres)
  gsn_text_ndc(wks, " < 80% of runs~C~ agree on sign", x2 + 0.005, 0.48, tlres)

  ; Left-side legend: not significant at 10% level
  pmres = pmres0
  pmres@gsFillScaleF = 0.8
  pmres@gsFillIndex = 6

  x1 = 0.20
  x2 = 0.22
  y1 = 0.47
  y2 = 0.49

  gsn_polyline_ndc(wks, (/x1, x2, x2, x1, x1/), (/y1, y1, y2, y2, y1/), lres)

  do j = 0, 2, 2
    do i = 0, 2
      gsn_polymarker_ndc(wks, x1 + (i + 0.5) * (x2 - x1) / 3., \
                              y1 + (j + 0.5) * (y2 - y1) / 3., res_marker)
    end do
  end do

  do j = 1, 1
    do i = 0, 1
      gsn_polymarker_ndc(wks, x1 + (i + 1.) * (x2 - x1) / 3., \
                              y1 + (j + 0.5) * (y2 - y1) / 3., res_marker)
    end do
  end do

  gsn_text_ndc(wks, " not significant~C~ at 10% level", x2 + 0.005, 0.48, tlres)


  frame(wks)
end
