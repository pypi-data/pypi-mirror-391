#ifndef DUNE_POLYGONGRID_INDEXSET_HH
#define DUNE_POLYGONGRID_INDEXSET_HH

#include <cassert>

#include <array>
#include <type_traits>

#include <dune/geometry/dimension.hh>
#include <dune/geometry/type.hh>

#include <dune/grid/common/gridenums.hh>
#include <dune/grid/common/indexidset.hh>

#include <dune/polygongrid/declaration.hh>
#include <dune/polygongrid/entity.hh>

namespace Dune
{

  namespace __PolygonGrid
  {

    // IndexSet
    // --------

    template< class ct >
    class IndexSet
      : public Dune::IndexSet< const PolygonGrid< ct >, IndexSet< ct >, std::size_t, std::array< GeometryType,1 > >
    {
      typedef IndexSet< ct > This;
      typedef Dune::IndexSet< const PolygonGrid< ct >, IndexSet< ct >, std::size_t, std::array< GeometryType,1 > > Base;

    public:
      static const int dimension = 2;

      typedef std::size_t Index;
      typedef typename Base::Types Types;

      template< int codim >
      struct Codim
      {
        typedef Dune::Entity< codim, 2, const PolygonGrid< ct >, __PolygonGrid::Entity > Entity;
      };

      IndexSet ( const Mesh< ct > &mesh, MeshType type )
      {
        size_[ 0 ] = mesh.numCells( type );
        size_[ 1 ] = mesh.numEdges( type );
        size_[ 2 ] = mesh.numVertices( type );
      }

      template< class Entity >
      Index index ( const Entity &entity ) const
      {
        return index< Entity::codimension >( entity );
      }

      template< int cd >
      Index index ( const typename Codim< cd >::Entity &entity ) const
      {
        return entity.impl().index();
      }

      template< class Entity >
      Index subIndex ( const Entity &entity, int i, int codim ) const
      {
        return subIndex< Entity::codimension >( entity, i, codim );
      }

      template< int cd >
      Index subIndex ( const typename Codim< cd >::Entity &entity, int i, int codim ) const
      {
        return entity.impl().subIndex( codim, i );
      }

      Index size ( GeometryType type ) const { return (type.isNone() ? size( dimension - type.dim() ) : 0u); }
      Index size ( int codim ) const { assert( (codim >= 0) && (codim <= dimension) ); return size_[ codim ]; }

      template< class Entity >
      bool contains ( const Entity &entity ) const
      {
        return true;
      }

      Types types ( int codim ) const noexcept { return {{ GeometryTypes::none( dimension - codim ) }}; }

    private:
      std::array< Index, dimension+1 > size_;
    };

  } // namespace __PolygonGrid

} // namespace Dune

#endif // #ifndef DUNE_POLYGONGRID_INDEXSET_HH
