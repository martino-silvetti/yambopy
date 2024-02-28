#!/miniconda3/envs/yambopy/bin/python3.11

from yambopy.dbs.latticedb import *
from yambopy.dbs.em1sdb import *
from yambopy.em1s.em1s_rotate import *
from yambopy.lattice import point_matching
from itertools import product
import math
import bisect
import time


#Re-implement Paleari's algorithm to fold the static screening of the primitive cell to the smaller supercell 1BZ'
# WARNING: Please use cartesian coordinates

class fold_vX():

  def __init__(self, UcLatticePath, UcScreeningPath, ScLatticePath, ScScreeningPath, UcRotatedXOutPath, ScRotatedXOutPath, UcLattDB ="ns.db1",UcEm1sDB = "ndb.em1s" ,ScLattDB = "ns.db1" ,ScEm1sDB = "ndb.em1s", ExpandUc=True, ExpandSc=True):
 
      #READ YAMBO DATABASES
      #read uc lattice points and screening database
      UcLattice = YamboLatticeDB.from_db_file(filename = UcLatticePath+UcLattDB, Expand=True)
      UcStatScreen = YamboStaticScreeningDB(save = UcLatticePath, em1s = UcScreeningPath )
      
      self.UcLattice = UcLattice
      self.UcStatScreen = UcStatScreen
      
      #read sc lattice points and screening database. Do not care if Sc computation is converged or correct. We just need the correct set of q points and g vectors
      ScLattice = YamboLatticeDB.from_db_file(filename = ScLatticePath+ScLattDB, Expand=True)
      ScStatScreen = YamboStaticScreeningDB(save = ScLatticePath, em1s = ScScreeningPath )

      self.ScLattice = ScLattice
      self.ScStatScreen = ScStatScreen
      

      # if screening databases are not already expanded from IBZ to the full 1BZ make the rotation
      print("Expand unit cell Q points")
      if ExpandUc == True :
          #expand the Uc static screening from IBZ to the full 1BZ by mean of a rotation
          UcFull1BZStaticScreening = YamboEm1sRotate(UcStatScreen, save_path = UcLatticePath , path_output_DBs = UcRotatedXOutPath)
      else :
          UcFull1BZStaticScreening = UcStatScreen
       
      print("Expand supercell q points")  
      if ExpandSc == True :
          #expand the Sc static screening from IBZ to the full 1BZ by mean of a rotation. Might give a problem with fixed dimensions to allocate via netcdf libraries
          ScFull1BZStaticScreening = YamboEm1sRotate(ScStatScreen, save_path = ScLatticePath , path_output_DBs = ScRotatedXOutPath)
      else : 
          ScFull1BZStaticScreening = ScStatScreen



      #PLOTS
      # uncomment plots if needed
      #self.PlotReciprocal(UcFull1BZStaticScreening.qpoints, ScFull1BZStaticScreening.car_qpoints , "Full 1BZ for unit and supercell","Unit cell","Supercell" )
#                                     A                                   A
#                                     |                                   |
#                                     |                                   |
#                          in cartesian coord                      in cartesian coord      
#                          exited by YamboEm1sRotate               exited from YamboStaticScreeningDB
#                          use:                                    use: 
#                             -> .qpoints for cartesian               -> .car_qpoints for cartesian
#                             -> reduced not provided                 -> .red_qpoints for reduced
        
#     Plot Q-points before and after rotation 
#     self.PlotReciprocal(UcFull1BZStaticScreening.qpoints, UcStatScreen.car_qpoints , "Unit cell 1BZ read from YamboStaticScreeningDB","rotated","not rotated" )
#     Plot q-points before and after rotation (only if rotation was needed. Here I'm using supercell calculations without symmetries, then rotation has not been carried out)
#     self.PlotReciprocal(ScFull1BZStaticScreening.car_qpoints, ScStatScreen.car_qpoints , "Supercell 1BZ read from YamboStaticScreeningDB","rotated","not rotated" )
#     plot Q and q points for comparison
#     self.PlotReciprocal(UcFull1BZStaticScreening.red_qpoints, ScFull1BZStaticScreening.red_qpoints , "Full 1BZ for unit and supercell","Unit cell","Supercell" )


      #EXTRACT NUMBER OF G, g, Q, q FROM DATABASES     
      # make available the G and Q arrays for the Uc epsilon 
      self.Gvectors = UcFull1BZStaticScreening.gvectors   # G vectors in cartesian coordinates 
      self.NGvectors = UcFull1BZStaticScreening.ngvectors
      self.Qpts = UcFull1BZStaticScreening.qpoints   # in cartesian coordinates
      self.NQpts = UcFull1BZStaticScreening.nqpoints
      self.UcX = UcFull1BZStaticScreening.X
      # At this point I have X_{G,G'}(Q) for the Uc with a database fragment for each Q

      # make available the g and q arrays for the Sc epsilon 
      self.gvectors = ScFull1BZStaticScreening.gvectors   # g vectors in cartesian coordinates
      self.Ngvectors = ScFull1BZStaticScreening.ngvectors
      self.qpts = ScFull1BZStaticScreening.car_qpoints
      self.Nqpts = ScFull1BZStaticScreening.nqpoints
      self.ScX = ScFull1BZStaticScreening.X
      # At this point I have the number of g vectors and q points for the Sc


      
      #print Q and q in cartesian coordinates
      print("****Q points processed by YamboEm1sRotate (after rotation)*************")
      print("Number of Q points: ", len(self.Qpts))
      print("Q points (cart.)")
#      print(self.Qpts)
      
      print("****q points read from YamboStaticScreenings***************************")
      print("Number of q points: ", len(self.qpts))
      print("q points (cart.)")
#      print(self.qpts)
      
      #print G and g 
      print("****G vectors*****")
      print("number of G vectors : ",  len(self.Gvectors))
      print("G vectors (cart)")
#      print(self.Gvectors)
      
      print("****g vectors*****")
      print("number of g vectors : ",  len(self.gvectors))
      print("g vectors (cart)")
#      print(self.gvectors)

      #MORE PLOTS FOR DEBUGGING 
      # Q and q points, set slice_at_gamma = True to have the Q and q points for Q_z = 0 and see the Gamma point, default =  True and see the Q and q points piled up along z
#      self.PlotReciprocal(self.Qpts, self.qpts , "Full 1BZ for unit and supercell","Unit cell","Supercell" , slice_at_gamma = True ) 
#      self.PlotReciprocal(self.gvectors,self.Gvectors, "G and g vectors", "g-vectors","G vectors")⎄
#      self.PlotReciprocal(self.gvectors,self.Qpts, "g and Q vectors", "g-vectors","Q points")
#      self.PlotReciprocal(self.gvectors,self.Gvectors, "G and g vectors", "g-vectors","G vectors")


      #RUN
      # find the g_Q that are equal to Q-q and return an array of [i,j,k] = [Index Q, Index q, Index g : g = g_Q = Q-q]      
      g_QIndexMap = self.Get_Qminusq()
      print("first list Q-q: ", g_QIndexMap.shape)   # (number of Q) times (number of q) 
#      print(g_QIndexMap)
      
      # find all the pairs G,g such that g = G + g_Q and return an array [i,j,k] = [Index G, Index g, Index g_Q]. 
      # Note that for a single g_Q there might be more than one (G,g) pair
      g_QMap = self.Getg_Q(g_QIndexMap)
      print("second list G+g_Q: ", g_QMap.shape)
      print(g_QMap)


      # for debugging: print all remapped [G,g,g_Q] to choose a G and a corresponding g to correctly plot 
      # the Unit cell remapped X_{G,G'} and the supercell X_{g,g'} as functions of |q| and see if they are the same 
#     print(g_QMap)
      
      
      # remap X_{g,g'}(q) = X_{G,G'}(Q) 
      X = self.RemapX(g_QIndexMap,g_QMap,self.UcX)
      print("Remapped X shape: ")
      print(X.shape)
      
      # plot X of folded unit cell vs X of supercell 
      self.PlotEm1sSc_vs_Exp(self.ScX,X, 72 , 68 , 72 , 68) 
      
      #plot X of folded unit cell vs X of unit cell (for the G and g that are in common)
      self.PlotEm1sUc_vs_Exp(self.UcX,X, 8 , 4, 72 , 68 )
      #                                  A  /    \   \      
      #                                  | /      \_  \
      #                                 put          put
      #                              G vector      g vector
      #                                here          here                                 
      
      print("Folded databases saved")


    
  
  def Get_Qminusq(self, threshold = 1E-6):
      # Acquire all the possible Q-q vectors
      # All_Q_minus_q = np.array( [[Q-q for q in self.qpts] for Q in self.Qpts] )
      Q_minus_q = self.Qpts[:,np.newaxis]-self.qpts #shape: (N Q points , N q points, 3 components)
      # Compute absolute differences with broadcasting
      QminusqDiffg = np.abs(Q_minus_q[:,:, np.newaxis] - self.gvectors) #shape: (N Q points, N q points, N g vectors, 3 components)
      # Check the condition for all elements to be below thr
      Condition_Qminusq_in_g = np.all(QminusqDiffg < threshold, axis=-1) #shape: (N Q points, N q points, N g vectors)
      # Find the indices where the condition is true
      IndicesQmqEqualg = np.nonzero(Condition_Qminusq_in_g) # tuple of three arrays of Q,q,g indices
      # Stack the indices along the last axis
      Qqg_qIndexMap = np.column_stack(IndicesQmqEqualg)# array of indices are ordered by Q,q,g
#     print(Qqg_qIndexMap)
      
      # returns the set of indices ijk which associate at each Q[i],q[j] pair the g[k] corresponding to Q[i]-q[j] IF AND ONLY IF such g[k] exists
      # This IF AND ONLY IF is why len(Qqg_qIndexMap) = N Q points and not  = (N Q points) times (N g vectors)
      return Qqg_qIndexMap 
  
  def Getg_Q(self, All_g_Q_indices, threshold = 1E-6):
      # Eliminate all the doubly counted indices of g_Qs that connect more than two pairs of Q-q
      g_Q_IndexCleanList = np.unique(All_g_Q_indices[:,2])
      print("elements in clean Q-q list: " , g_Q_IndexCleanList.shape)
      print(g_Q_IndexCleanList)  
      # Acquire all the g_Qs corresponding to the left over indices
      g_Q = np.array([self.gvectors[i] for i in g_Q_IndexCleanList])
      Gplusg_Q = self.Gvectors[:,np.newaxis]+g_Q   # Gplusg_Q array of shape (number of G vectors) times (number of not doubly counted g_Q) 
      start3 = time.time()
      Ggg_QMap = []
      for IndexG in range(len(Gplusg_Q)):
          for Indexg_Q in range(len(Gplusg_Q[0])):
              for Indexg in range(len(self.gvectors)):
                  if (abs(Gplusg_Q[IndexG,Indexg_Q]-self.gvectors[Indexg]) < threshold).all() :  #abs does not include the shorter ones too 
                       Ggg_QMap.append([IndexG,Indexg,Indexg_Q])
      Ggg_QMap = np.array(Ggg_QMap)
      print("time elapsed for the long computation: ", time.time()-start3)


      #uncomment this section for debugging: recast the indices of the g vectors found as rows (each row is a G i.e. G+g_Q at G fixed) and columns (g_Q)
      #this recast is only useful in case one wants to compare this function with the output of the Get_g_Q_KDTree.
      #The problem with Get_g_Q_KDTree is that it makes use of KDTree in point_matching, meaning that it finds the g 
      #that is the closest to G+g_Q, which is not necessarily the one that is "equal" to G+g_Q (in a tolerance interval). Here G and g_Q not connected by
      #any g vector are mearked as "nf" not found
      print("recast")
      b = []
      for IndexG in range(len(self.Gvectors)):
          a = []
          for index in range(len(Ggg_QMap)):
               if Ggg_QMap[index,0] == IndexG :
                  a.append(Ggg_QMap[index,1])
          b.append(a)
      for i in range(len(b)):
          print(b[i], "lenght: ", len(b[i]))

      return Ggg_QMap   # output is organized as [IndexG, Index g, Index g_Q]


  def RemapX(self, IndexMap, g_QMap, UcX):
      
      # allocate complex X 
      ExpandedX = np.zeros([self.Nqpts,self.Ngvectors,self.Ngvectors],dtype=np.complex64) # shape: (number of q, number of g, number of g)
 
      # for each Q,q in the clean list associate the g_Q with the corresponding G,g pairs from Getg_Q
      for IndexQ in range(self.NQpts):
          g_Q = IndexMap[IndexQ,2] # g_Q from first list (calculated as Q-q)
          Indexq = IndexMap[IndexQ,1]   # 
          G_and_g = g_QMap[g_QMap[:,2] == g_Q]   # select the G,g pairs such that g-G are equal to the g_Q computed as Q-q
          for j1,j2 in product(range(len(G_and_g)),repeat=2):
          #for j1 in range(len(G_and_g)):
                #j2=j1
              IndexG1, IndexG2 = G_and_g[j1,0], G_and_g[j2,0]
              Indexg1, Indexg2 = G_and_g[j1,1], G_and_g[j2,1]
              ExpandedX[Indexq,Indexg1,Indexg2] = UcX[IndexQ,IndexG1,IndexG2] 
      return ExpandedX   


  def PlotReciprocal(self, SetQ1, SetQ2, title, label1, label2, slice_at_gamma = False) : 
      
      ax = plt.gca()
      ax.set_title(title)
    
      ax.set_aspect('equal')
      
      if slice_at_gamma == True : 
         SliceQ1X = SetQ1[SetQ1[:,2]==0,0]
         SliceQ1Y = SetQ1[SetQ1[:,2]==0,1]
      else :
         SliceQ1X = SetQ1[:,0]
         SliceQ1Y = SetQ1[:,1]
      
      if slice_at_gamma == True : 
         SliceQ2X = SetQ2[SetQ2[:,2]==0,0]
         SliceQ2Y = SetQ2[SetQ2[:,2]==0,1]
      else :
         SliceQ2X = SetQ2[:,0]
         SliceQ2Y = SetQ2[:,1]
      
      ax.scatter(SliceQ1X,SliceQ1Y,marker='H',s=200,color='teal',\
               linewidth=0.5,edgecolors='black',label=label1)

      ax.scatter(SliceQ2X,SliceQ2Y,marker='H',s=50,color='orange',\
               linewidth=0.5,edgecolors='black',label=label2)
      plt.legend()
      plt.show()

  def PlotEm1sSc_vs_Exp(self,ScX, ExpandedX, Indexg1_orig = 0, Indexg2_orig = 0 , Indexg1_expand = 0 , Indexg2_expand = 0):   # copypasted from em1sdb
        
      ScListModq =  [np.linalg.norm(q) for q in self.qpts]
      ExpandedListModQ = [np.linalg.norm(q) for q in self.qpts]

      ScXNormq = np.zeros([self.Nqpts,self.Ngvectors,self.Ngvectors],dtype=np.complex64)
      ExpandedXNormq = np.zeros([self.Nqpts,self.Ngvectors,self.Ngvectors],dtype=np.complex64)
        
      ScXNormq = [xq[Indexg1_orig,Indexg2_orig] for xq in ScX ] 
      ExpandedXNormQ = [xq[Indexg1_expand,Indexg2_expand] for xq in ExpandedX ]

      #order according to the distance
      ScListModq,  ScXNormq = list(zip(*sorted(zip(ScListModq, ScXNormq))))
      ScXNormq = np.array(ScXNormq)

      ExpandedListModQ , ExpandedXNormQ =  list(zip(*sorted(zip(ExpandedListModQ , ExpandedXNormQ ))))
      ExpandedXNormQ = np.array(ExpandedXNormQ)
  
      axReal = plt.gca()        
      axReal.plot(ScListModq,ScXNormq.real, marker = "o", markersize = 4 , label = "original SC")
      axReal.plot(ExpandedListModQ,ExpandedXNormQ.real, marker = "x", markersize = 20 , linestyle = "none"  , label = "expanded UC")
      axReal.set_xlabel('$|q|$')
      axReal.set_ylabel('Re$\epsilon^{-1}_{%d%d}(\omega=0)$'%(Indexg1_expand,Indexg2_expand))
      axReal.legend()
      plt.show()
        
        
      axImag = plt.gca()        
      axImag.plot(ScListModq,ScXNormq.imag, marker = "o", markersize = 4, label = "original SC" )
      axImag.plot(ExpandedListModQ,ExpandedXNormQ.imag , marker = "x", markersize = 20 , linestyle = "none" , label = "expanded UC")
      axImag.set_xlabel('$|q|$')
      axImag.set_ylabel('Im$\epsilon^{-1}_{%d%d}(\omega=0)$'%(Indexg1_expand,Indexg2_expand))
      plt.legend()
      plt.show()

  def PlotEm1sUc_vs_Exp(self,UcX, ExpandedX, IndexG1 = 0, IndexG2 = 0 , Indexg1=0,Indexg2=0):   # copypasted from em1sdb
        
      UcXNormQ = np.zeros([self.NQpts,self.NGvectors,self.NGvectors],dtype=np.complex64)
      ExpandedXNormq = np.zeros([self.Nqpts,self.Ngvectors,self.Ngvectors],dtype=np.complex64)

      UcListModQ =  [np.linalg.norm(Q) for Q in self.Qpts]
      ExpandedListModq = [np.linalg.norm(q) for q in self.qpts]
        
      UcXNormQ = [xq[IndexG1,IndexG2] for xq in UcX ] 
      ExpandedXNormq = [xq[Indexg1,Indexg2] for xq in ExpandedX ]

       #order according to the distance
      UcListModQ,  UcXNormQ = list(zip(*sorted(zip(UcListModQ, UcXNormQ))))
      UcXNormQ = np.array(UcXNormQ)

      ExpandedListModq , ExpandedXNormq =  list(zip(*sorted(zip(ExpandedListModq , ExpandedXNormq ))))
      ExpandedXNormq = np.array(ExpandedXNormq)
  
      axReal = plt.gca()        
      axReal.plot(UcListModQ, UcXNormQ.real, marker = "o", markersize = 4 , label = "UC Unexpanded")
      axReal.plot(ExpandedListModq,ExpandedXNormq.real , label = "UC expanded", marker = "x", markersize = 20, linestyle = "none")
      axReal.set_xlabel('$|q|$')
      axReal.set_ylabel('Re$\epsilon^{-1}_{%d%d}(\omega=0)$'%(Indexg1,Indexg2))
      plt.legend()
      plt.show()
        
        
      axImag = plt.gca()        
      axImag.plot(UcListModQ,UcXNormQ.imag, marker = "o", markersize = 4, label = "UC Unexpanded")
      axImag.plot(ExpandedListModq,ExpandedXNormq.imag, label = "UC expanded", marker = "x", markersize = 20, linestyle = "none")
      axImag.set_xlabel('$|q|$')
      axImag.set_ylabel('Im$\epsilon^{-1}_{%d%d}(\omega=0)$'%(Indexg1,Indexg2))
      plt.legend()
      plt.show()



  def Get_g_Q_KDTree(self, All_g_Q_indices):
      # Eliminate all the doubly counted indices of g_Qs that connect more than two pairs of Q-q
      g_Q_IndexCleanList = np.unique(All_g_Q_indices[:,2])
      #print(g_Q_IndexCleanList)  
      # Acquire all the g_Qs corresponding to the left over indices
      g_Q = np.array([self.gvectors[i] for i in g_Q_IndexCleanList])
 
      start2 = time.time()  

      Gplusg_Q = self.Gvectors[:,np.newaxis]+g_Q   # Gplusg_Q array of shape (number of G vectors) times (number of not doubly counted g_Q) 
      print(Gplusg_Q.shape)
      IndexList = []
      for GpgQ in Gplusg_Q: # i.e. for each G
             # point_matching(a,b,double_check) returns an array of lenght len(b) of elements p[i] such that a[p] is the one that
             # is the closest to element b[i]
             IndexList.append(point_matching(self.gvectors,GpgQ, double_check = False)) 
      print("time2 : ", time.time()-start2)
      
      return np.array(IndexList) # returns the indices of g vectors in an array of shape (number of G vectors) times (number of g_Q)

   # method to do exactly the same as Getg_Q but with inline operations. It is slower than Getg_Q   
#  def Getg_Q_heavy(self, All_g_Q_indices, threshold = 1E-6):  #inline operations take more time than nested for loops
#      # Eliminate all the doubly counted indices of g_Qs that connect more than two pairs of Q-q
#      g_Q_IndexCleanList = np.unique(All_g_Q_indices[:,2])
#      print("elements in clean Q-q list: ",g_Q_IndexCleanList.shape)
#      g_Q = np.array([self.gvectors[i] for i in g_Q_IndexCleanList])
#      Gplusg_Q = self.Gvectors[:,np.newaxis]+g_Q   # Gplusg_Q array of shape (number of G vectors) times (number of not doubly counted g_Q) 
#      start4 = time.time()
#      Ggg_QMap = np.array([ [IndexG,Indexg,Indexg_Q] for IndexG in range(len(Gplusg_Q)) for Indexg_Q in range(len(Gplusg_Q[0])) for Indexg in range(len(self.gvectors))  if (abs(Gplusg_Q[IndexG,Indexg_Q]-self.gvectors[Indexg]) < threshold).all() ]) 
#      print("time elapsed for the short computation: ", time.time()-start4)
#      print(Ggg_QMap.shape)
#      return Ggg_QMap   # output is organized as [IndexG, Index g, Index g_Q]




"example of output"
""" 
[[ 0  0  0]
 [ 0  1  1]
 [ 0  2  2]
 [ 0  3  3]
 [ 0  4  4]
 [ 0  5  5]
 [ 0  6  6]
 [ 0  7  7]
 [ 0  8  8]
 [ 0 11  9]
 [ 0 13 10]
 [ 0 14 11]
 [ 0 15 12]
 [ 0 16 13]
 [ 0 17 14]
 [ 0 18 15]
 [ 0 19 16]
 [ 0 20 17]
 [ 0 21 18]
 [ 0 22 19]
 [ 1  9  0]
 [ 1 35  1]
 [ 1  1  2]
 [ 1 23  3]
 [ 1 25  4]
 [ 1 27  5]
 [ 1 29  6]
 [ 1 31  7]
 [ 1 33  8]
 [ 1 55  9]
 [ 1 57 10]
 [ 1 13 11]
 [ 1 59 12]
 [ 1 15 13]
 [ 1 61 14]
 [ 1 17 15]
 [ 1 63 16]
 [ 1 19 17]
 [ 1 65 18]
 [ 1 21 19]
 [ 2 10  0]
 [ 2  2  1]
 [ 2 36  2]
 [ 2 24  3]
 [ 2 26  4]
 [ 2 28  5]
 [ 2 30  6]
 [ 2 32  7]
 [ 2 34  8]
 [ 2 12  9]
 [ 2 14 10]
 [ 2 58 11]
 [ 2 16 12]
 [ 2 60 13]
 [ 2 18 14]
 [ 2 62 15]
 [ 2 20 16]
 [ 2 64 17]
 [ 2 22 18]
 [ 2 66 19]
 [ 3 67  0]
 [ 3 37  6]
 [ 3 38  7]
 [ 3  3  8]
 [ 3 43 14]
 [ 3 44 15]
 [ 3 45 16]
 [ 3 46 17]
 [ 3 11 18]
 [ 3 12 19]
 [ 4 68  0]
 [ 4 37  5]
 [ 4  4  7]
 [ 4 39  8]
 [ 4 43 12]
 [ 4 44 13]
 [ 4 13 16]
 [ 4 14 17]
 [ 4 47 18]
 [ 4 48 19]
 [ 5 69  0]
 [ 5 38  4]
 [ 5  5  6]
 [ 5 40  8]
 [ 5 45 10]
 [ 5 46 11]
 [ 5 15 14]
 [ 5 16 15]
 [ 5 49 18]
 [ 5 50 19]
 [ 6 70  0]
 [ 6 39  3]
 [ 6  6  5]
 [ 6 41  7]
 [ 6 47  9]
 [ 6 17 12]
 [ 6 18 13]
 [ 6 51 16]
 [ 6 52 17]
 [ 7 71  0]
 [ 7 40  3]
 [ 7  7  4]
 [ 7 42  6]
 [ 7 49  9]
 [ 7 19 10]
 [ 7 20 11]
 [ 7 53 14]
 [ 7 54 15]
 [ 8 72  0]
 [ 8  8  3]
 [ 8 41  4]
 [ 8 42  5]
 [ 8 21  9]
 [ 8 51 10]
 [ 8 52 11]
 [ 8 53 12]
 [ 8 54 13]]



[0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22] lenght:  20
[9, 35, 1, 23, 25, 27, 29, 31, 33, 55, 57, 13, 59, 15, 61, 17, 63, 19, 65, 21] lenght:  20
[10, 2, 36, 24, 26, 28, 30, 32, 34, 12, 14, 58, 16, 60, 18, 62, 20, 64, 22, 66] lenght:  20
[67, 37, 38, 3, 43, 44, 45, 46, 11, 12] lenght:  10
[68, 37, 4, 39, 43, 44, 13, 14, 47, 48] lenght:  10
[69, 38, 5, 40, 45, 46, 15, 16, 49, 50] lenght:  10
[70, 39, 6, 41, 47, 17, 18, 51, 52] lenght:  9
[71, 40, 7, 42, 49, 19, 20, 53, 54] lenght:  9
[72, 8, 41, 42, 21, 51, 52, 53, 54] lenght:  9
second list G+g_Q:  (117, 3)

(9, 20, 3)
time2 :  0.003187894821166992
con KDTree: 
[[ 0  1  2  3  4  5  6  7  8 11 13 14 15 16 17 18 19 20 21 22]
 [ 9 35  1 23 25 27 29 31 33 55 57 13 59 15 61 17 63 19 65 21]
 [10  2 36 24 26 28 30 32 34 12 14 58 16 60 18 62 20 64 22 66]
 [67 67 67 67 37 38 37 38  3 67 43 44 45 46 43 44 45 46 11 12]
 [68 68 68 37 68 37 39  4 39 43 68 68 43 44 47 48 13 14 47 48]
 [69 69 69 38 38 69  5 40 40 45 45 46 69 69 15 16 49 50 49 50]
 [70 70 70 39 39  6 70 41 41 47 47 48 17 18 70 70 51 52 51 52]
 [71 71 71 40  7 40 42 71 42 49 19 20 49 50 53 54 71 71 53 54]
 [72 72 72  8 41 42 41 42 72 21 51 52 53 54 51 52 53 54 72 72]]


"""


