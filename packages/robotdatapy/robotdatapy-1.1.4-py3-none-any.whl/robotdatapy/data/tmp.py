import gtsam
for d in gtsam.__dir__():
    print(d)

p = gtsam.PoseTranslationPrior3D()
print(p)
