library(yaml)
library(rgl)

loadgmm = function(gmmdata) {
  data = as.double( gmmdata$data )
  nr_gauss = gmmdata$cols / 13

  #print(nr_gauss)

  weights <- data[1:nr_gauss]
  #print(weights)

  means <- data[(nr_gauss+1):(nr_gauss + nr_gauss*3)]
  #print(means)
  
  covs <- data[(nr_gauss*4+1):gmmdata$cols]
  #print(covs)

  gmm = list()

  for (i in 1:nr_gauss) 
  {
    #print(i)
    cur_weight = weights[i]
    cur_mean = means[(1 + (i-1) * 3):(i * 3)]
    cur_cov = matrix(covs[(1 + (i-1) * 9):(i * 9)], ncol=3)
    #list()
    #print(cur_weight)
    #print(cur_mean)
    #print(cur_cov)
    gauss = list(weight=cur_weight, mean=cur_mean, cov=cur_cov)
    #print(gauss)
    
    gmm = c(gmm, list(gauss))
  }
  #print(gmm)
  
  return(gmm)
}

ellipsoid3d <- function(rx=1,ry=1,rz=1,n=30,ctr=c(0,0,0),
                        qmesh=FALSE,
                        trans = par3d("userMatrix"),...) {
  if (missing(trans) && !rgl.cur()) trans <- diag(4)
  degvec <- seq(0,2*pi,length=n)
  ecoord2 <- function(p) {
    c(rx*cos(p[1])*sin(p[2]),ry*sin(p[1])*sin(p[2]),rz*cos(p[2])) }
  v <- apply(expand.grid(degvec,degvec),1,ecoord2)
  if (qmesh) v <- rbind(v,rep(1,ncol(v))) ## homogeneous
  e <- expand.grid(1:(n-1),1:n)
  i1 <- apply(e,1,function(z)z[1]+n*(z[2]-1))
  i2 <- i1+1
  i3 <- (i1+n-1) %% n^2 + 1
  i4 <- (i2+n-1) %% n^2 + 1
  i <- rbind(i1,i2,i4,i3)
  if (!qmesh)
    quads3d(v[1,i],v[2,i],v[3,i],...)
  else return(rotate3d(qmesh3d(v,i,material=...),matrix=trans))
}

display_cov <- function(gauss) {
    means = gauss$mean
    cov = gauss$cov
    weight = gauss$weight
    sphere <- ellipsoid3d(2,2,2,qmesh=TRUE) 
    ellipsoid <- translate3d(rotate3d(sphere,matrix=chol(cov)*qnorm(0.975)), 
                                         means[1],means[2],means[3]) 
    shade3d(ellipsoid, color=rgb(means[3],means[2],means[1], maxColorValue=255), alpha=weight) 
}


args <- commandArgs(TRUE)

filename  <- args[1]

#filename = "~/da/images/flowers/10_8_s.bmp.grabcut-output.yml"

y = yaml.load_file(filename)

#y$bgdModel

bgdGMM <- loadgmm(y$bgdModel)
fgdGMM <- loadgmm(y$fgdModel)

for(i in 1:5) {
    display_cov(bgdGMM[[i]])
    display_cov(fgdGMM[[i]])
}

axes3d()
decorate3d(255,255,255)

 #
 # create animation
 #
 
 rgl.bringtotop()
 rgl.viewpoint(0,20)
 
 setwd("/home/goering")
 for (i in 1:45) {
   rgl.viewpoint(i,20)
   filename <- paste("pic",formatC(i,digits=1,flag="0"),".png",sep="")
   rgl.snapshot(filename)
 }

system("convert -delay 10 pic*png -loop 0 pic.gif")

 ## Now run ImageMagick command:
 ##    convert -delay 10 *.png -loop 0 pic.gif
 ## End(Not run)


#invisible(readLines("stdin", n=1))

#print(bgdGMM)

