import cv2
import numpy as np

def template_matching(img, tmpl):
    match = cv2.matchTemplate(img, tmpl, cv2.TM_CCOEFF_NORMED)
    (_, maxval, _, maxloc) = cv2.minMaxLoc(match)
    return (maxval, maxloc)

def build_pyramid(img, max_level):
    pyramid = [img]
    for i in range(0, max_level+1):
        pyramid.append(cv2.pyrDown(pyramid[i]))

    return pyramid

def fast_template_matching(img, tmpl, max_level):
    pyr_img = build_pyramid(img, max_level)
    pyr_tmpl = build_pyramid(tmpl, max_level)

    results = []
    for level in range(max_level,-1,-1):
        ref = pyr_img[level]
        tpl = pyr_tmpl[level]
        
        if level == max_level:
            results.append(cv2.matchTemplate(ref, tpl, cv2.TM_CCOEFF_NORMED))
        else:
            mask = cv2.pyrUp(results[-1])
            (_, maxval, _, maxloc) = cv2.minMaxLoc(mask)
            if maxval < 0.5:
                break
            #print maxloc
            mask_h, mask_w = mask.shape
            mask_w = mask_w / 50
            mask_h = mask_h / 50
            tpl_h, tpl_w = tpl.shape
            y = maxloc[1] - mask_h/2
            x = maxloc[0] - mask_w/2
            w = mask_w + tpl_w
            h = mask_h + tpl_h
            res = np.zeros(ref.shape, np.float32)
            if x+w > ref.shape[1] or y+h > ref.shape[0] or x < 0 or y < 0:
                # Out of bounds
                return (0,(0,0))
            
            res[y:y+mask_h+1,x:x+mask_w+1] = cv2.matchTemplate(ref[y:y+h,x:x+w], tpl, cv2.TM_CCOEFF_NORMED)
            results.append(res)

    (_, maxval, _, maxloc) = cv2.minMaxLoc(results[-1])
    return maxval, maxloc
            




