#ifndef DUNE_POLYGONGRID_CAPABILITIES_HH
#define DUNE_POLYGONGRID_CAPABILITIES_HH

#include <dune/grid/common/capabilities.hh>

#include <dune/polygongrid/declaration.hh>

namespace Dune
{

  namespace Capabilities
  {

    template< class ct, int codim >
    struct hasEntity< PolygonGrid< ct >, codim >
    {
      static const bool v = true;
    };

    template< class ct, int codim >
    struct hasEntityIterator< PolygonGrid< ct >, codim >
     : public hasEntity< PolygonGrid< ct >, codim >
    {
    };

    template< class ct >
    struct isCartesian< PolygonGrid< ct > >
    {
      static const bool v = false;
    };

    template< class ct >
    struct isLevelwiseConforming< PolygonGrid< ct > >
    {
      static const bool v = true;
    };

    template< class ct >
    struct isLeafwiseConforming< PolygonGrid< ct > >
    {
      static const bool v = true;
    };

    template< class ct, int codim >
    struct canCommunicate< PolygonGrid< ct >, codim >
    {
      static const bool v = false;
    };

    template< class ct >
    struct threadSafe< PolygonGrid< ct > >
    {
      static const bool v = false;
    };

    template< class ct >
    struct viewThreadSafe< PolygonGrid< ct > >
    {
      // this might be a problem but to our
      // knowledge the grid is thread safe
      static const bool v = true;
    };

    template< class ct >
    struct hasBackupRestoreFacilities< PolygonGrid< ct > >
    {
      static const bool v = false;
    };

  } // namespace Capabilities

} // namespace Dune

#endif // #ifndef DUNE_POLYGONGRID_CAPABILITIES_HH
