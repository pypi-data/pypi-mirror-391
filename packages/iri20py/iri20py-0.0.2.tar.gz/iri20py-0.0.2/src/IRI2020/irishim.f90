subroutine iri20_init(direct)
   implicit none
   character(len=*), intent(in) :: direct
   call read_ig_rz(direct)
   call readapf107(direct)
end subroutine

subroutine iri20_eval(jf,jmag,alat,alon,iyyy,mmdd,dhour,zkm,nzkm,outf,oarr,direct,logfile)
   implicit none
   logical, intent(in) :: jf(50), jmag
   real, intent(in) :: alat, alon, dhour, zkm(nzkm)
   real, intent(inout) :: outf(20, nzkm), oarr(100)
   integer, intent(in) :: iyyy, mmdd, nzkm
   character(len=*), intent(in) :: direct
   character(len=*), intent(in) :: logfile
   integer :: j
   call iri_sub(jf, jmag, alat, alon, iyyy, mmdd, dhour, zkm, nzkm, outf, oarr, direct, &
      logfile)
   if (jf(22)) then
      do j=5,13
         outf(j,:) = outf(j,:)*outf(1,:) / 100.0 ! % to absolute units
      end do
   endif
end subroutine
