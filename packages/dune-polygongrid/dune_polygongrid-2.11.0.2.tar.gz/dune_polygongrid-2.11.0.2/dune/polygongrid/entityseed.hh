#ifndef DUNE_POLYGONGRID_ENTITYSEED_HH
#define DUNE_POLYGONGRID_ENTITYSEED_HH

#include <cstddef>

#include <limits>
#include <type_traits>

#include <dune/grid/common/entityseed.hh>

namespace Dune
{

  namespace __PolygonGrid
  {

    // EntitySeed
    // ----------

    template< class Index, int codim >
    class EntitySeed
    {
      typedef EntitySeed< Index, codim > This;

    public:
      static const int codimension = codim;

      EntitySeed () = default;
      explicit EntitySeed ( const Index &index ) : index_( index ) {}

      bool isValid () const noexcept { return static_cast< bool >( index() ); }

      bool operator== ( const This &other ) const noexcept { return (index() == other.index()); }
      bool operator!= ( const This &other ) const noexcept { return (index() != other.index()); }

      Index index () const noexcept { return index_; }

    private:
      Index index_;
    };

  } // namespace __PolygonGrid

} // namespace Dune

#endif // #ifndef DUNE_POLYGONGRID_ENTITYSEED_HH
