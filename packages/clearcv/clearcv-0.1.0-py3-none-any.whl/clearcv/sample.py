import clearcv as ccv


img = ccv.io.imread('input.ppm') # use PPM or install imageio for PNG/JPG
gray = ccv.color.rgb2gray(img)
edges = ccv.filters.sobel(gray)
ccv = ccv.utils.normalize(edges)
ccv.io.imwrite('out.ppm', edges)