program iritest
   implicit none
   logical jf(50)
   integer i

   real :: zkm(250), outf(20, 250), oarr(50)

   do i = 1, 50
      jf = .true.
   enddo

!    defaults for jf(1:50)
!          jf(1)=.false.      ! f=no electron densities (t)
!          jf(2)=.false.      ! f=no temperatures (t)
!          jf(3)=.false.      ! f=no ion composition (t)
   jf(4)=.false.      ! t=B0table f=other models (f)
   jf(5)=.false.      ! t=CCIR  f=URSI foF2 model (f)
   jf(6)=.false.      ! t=DS95+DY85   f=RBV10+TBT15 (f)
!          jf(7)=.false.      ! t=tops f10.7<188 f=unlimited (t)
!          jf(8)=.false.      ! t=foF2	f=user input (t)
!          jf(9)=.false.      ! t=tops f10.7<188 f=unlimited (t)
!          jf(10)=.false.     ! t=Te standard f=using Ne user input (t)
!          jf(11)=.false.     ! t=Ne standard f=Lay-function (t)
           jf(12)=.false.     ! t=messages to unit 6 f=messages.txt on 11 (t)
!          jf(13)=.false.     ! t=foF1 f=foF1 or NmF1 user input (t)
!          jf(14)=.false.     ! t=hmF1 f=user input (only Lay version) (t)
!          jf(15)=.false.     ! t=foE f= foE or NmE user input (t)
!          jf(16)=.false.     ! t=hmE f=hmE user input (t)
!          jf(17)=.false.     ! t=Rz12 from file f=user input (only Lay version) (t)
!          jf(18)=.false.     ! t=IGRF dip,magbr,modip f=POGO68/10 for 1973(t)
!          jf(19)=.false.     !F1 prob model   only if foF1>0 and not NIGHT (t)
!          jf(20)=.false.     !standard F1  standard F1 plus L condition  (t)
! (19,20) = (t,t) f1-prob, (t,f) f1-prob-L, (f,t) old F1, (f,f) no F1
!          jf(21)=.false.     ! t=ion drift computed f=not comp.(t)
!          jf(22)=.false.     ! ion densities in m-3 (t)
   jf(23)=.false.     ! t=AEROS/ISIS f=TTS Te with PF10.7 (f)
!          jf(24)=.false.     ! t=D-reg-IRI-1990 f=FT-2001 (t)
!          jf(25)=.false.     ! t=F107D from APF107.DAT  f=user (t)
!          jf(26)=.false.     ! t=STORM model on   f= off (t)
!          jf(28)=.false.     ! t=spread-F computed f=not comp. (f)
!          jf(29)=.false.     ! t=old  f=New Topside options (t)
   jf(30)=.false.     ! t=corr f=NeQuick topside (f)
! (29,30) = (t,t) IRIold, (f,t) IRIcor, (f,f) NeQuick, (t,f) COR2
!          jf(31)=.false.     ! t=B0ABT f=Gulyaeva (t)
!          jf(32)=.false.     ! t=F107_81 from APF107.DAT  f=user (t)
   jf(33)=.false.     ! t=auroral boundary   f=off (f)
           jf(34)=.true.     ! t=messages on f= off (t)
   jf(35)=.false.     ! t=auroral E-storm model on f=off (f)
!          jf(36)=.false.     ! t=hmF2 w/out foF2_storm f=with (t)
!          jf(37)=.false.     ! t=topside w/out foF2_storm f=with (t)
!          jf(38)=.false.     ! t=WRITEs off in IRIFLIP f=on (t)
   jf(39)=.false.     ! t=M3000F2 model f=new hmF2 models (f)
   jf(40)=.false.     ! t=AMTB-model, f=Shubin-COSMIC model (f)
!          jf(41)=.false.     ! t:COV=F10.7_386 f:COV=f(IG12) (t)
!          jf(42)=.false.     ! t/f=Te w/o PF10.7 dependance (t)
!          jf(43)=.false.     ! t= B0 model f= B0 user input (t)
!          jf(44)=.false.     ! t= B1 model f= B1 user input (t)
!          jf(45)=.false.     ! t= Es occ. probability, f= off (t)
!          jf(46)=.false.     ! t= Es occ w/o solar/mag depend (t)
   jf(47)=.false.     ! t=CGM on  f=CGM off (f)
!          jf(48)=.false.     ! t=Ozhogin plasmasphere  f=Gallagher (t)
!          jf(49)=.false.     ! t=Ti-Tru2021 f=Ti-Bil1981 (t)
!          jf(50)=.false.     ! t=without plasmapause f=with plasmapause (t)

   do i=1, 250
      zkm(i) = 60 + (1000 - 60)*tanh(i*3.14/250.0)
   end do

   call iri20_init('src/IRI2020/data')
   call iri20_eval(jf, 0, 40, 105, 2022, -80, (43200.0/3600)+25, zkm, 250, outf, oarr, &
   'src/IRI2020/data', 'test.txt')
end program
