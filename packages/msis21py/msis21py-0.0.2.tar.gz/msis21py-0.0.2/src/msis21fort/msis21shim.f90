subroutine msis21py_init(parmpath,parmfile,switch_legacy)
   use msis_init, only          : msisinit
   implicit none
   character(len=*), intent(in), optional    :: parmpath                 !Path to parameter file
   character(len=*), intent(in), optional    :: parmfile                 !Parameter file name
   real(4), intent(in), optional             :: switch_legacy(1:25)      !Legacy switch array
   call msisinit(parmpath=parmpath,parmfile=parmfile,&
      switch_legacy=switch_legacy)
end subroutine

subroutine msis21py_eval(iyd,sec,alt,glat,glong,stl,f107a,f107,ap,&
   mass,d,t,exot,nalt)
   implicit none
   ! MSIS Legacy subroutine arguments
   integer, intent(in)         :: iyd
   real(4), intent(in)         :: sec
   real(4), intent(in)         :: alt(nalt)
   real(4), intent(in)         :: glat
   real(4), intent(in)         :: glong
   real(4), intent(in)         :: stl
   real(4), intent(in)         :: f107a
   real(4), intent(in)         :: f107
   real(4), intent(in)         :: ap(7)
   integer, intent(in)         :: mass, nalt
   real(4), intent(inout)      :: d(10,nalt), t(nalt)
   real(4), intent(out)        :: exot
   integer                     :: i
   real(4)                     :: tmpd(10), tmpt(2)
   do i=1,nalt
      call gtd8d(iyd, sec, alt(i), glat, glong, stl, f107a, f107, &
         ap, mass, tmpd, tmpt)
      t(i)=tmpt(2)
      d(:,i)=tmpd(:)
   end do
   exot = tmpt(1)
end subroutine
