#ifndef DUNE_POLYGONGRID_IDSET_HH
#define DUNE_POLYGONGRID_IDSET_HH

#include <type_traits>

#include <dune/geometry/dimension.hh>

#include <dune/grid/common/indexidset.hh>

#include <dune/polygongrid/declaration.hh>
#include <dune/polygongrid/entity.hh>
#include <dune/polygongrid/meshobjects.hh>

namespace Dune
{

  namespace __PolygonGrid
  {

    // IdSet
    // -----

    template< class ct >
    class IdSet
      : public Dune::IdSet< const PolygonGrid< ct >, IdSet< ct >, std::size_t >
    {
      typedef IdSet< ct > This;
      typedef Dune::IdSet< const PolygonGrid< ct >, This, std::size_t > Base;

    public:
      typedef std::size_t Id;

      static const int dimension = 2;

      template< int codim >
      struct Codim
      {
        typedef Dune::Entity< codim, 2, const PolygonGrid< ct >, __PolygonGrid::Entity > Entity;
      };

    public:
      template< class Entity >
      Id id ( const Entity &entity ) const
      {
        return id< Entity::codimension >( entity );
      }

      template< int codim >
      Id id ( const typename Codim< codim >::Entity &entity ) const
      {
        return id( entity.impl().index(), codim );
      }

      template< class Entity >
      Id subId ( const Entity &entity, int i, int codim ) const
      {
        return subId< Entity::codimension >( entity, i, codim );
      }

      template< int cd >
      Id subId ( const typename Codim< cd >::Entity &entity, int i, int codim ) const
      {
        return id( entity.impl().subIndex( codim, i ), codim );
      }

    private:
      static constexpr Id id ( std::size_t index, std::size_t codim ) noexcept { return (index << 2) | codim; }
    };

  } // namespace __PolygonGrid

} // namespace Dune

#endif // #ifndef DUNE_POLYGONGRID_IDSET_HH
