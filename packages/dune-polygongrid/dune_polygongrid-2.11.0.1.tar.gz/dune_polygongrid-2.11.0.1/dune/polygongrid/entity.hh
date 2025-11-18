#ifndef DUNE_POLYGONGRID_ENTITY_HH
#define DUNE_POLYGONGRID_ENTITY_HH

#include <cassert>

#include <exception>
#include <type_traits>

#include <dune/grid/common/entity.hh>

#include <dune/geometry/dimension.hh>

#include <dune/grid/common/entity.hh>
#include <dune/grid/common/entityiterator.hh>

#include <dune/polygongrid/entityseed.hh>
#include <dune/polygongrid/geometry.hh>
#include <dune/polygongrid/subentity.hh>

namespace Dune
{

  namespace __PolygonGrid
  {

    // Internal Forward Declarations
    // -----------------------------

    template< int codim, int dim, class Grid >
    class Entity;



    // External Forward Declarations
    // -----------------------------

    template< int codim, class Grid >
    class EntityIterator;



    // BasicEntity
    // -----------

    template< int codim, class Item, class Grid >
    class BasicEntity
    {
      typedef BasicEntity< codim, Item, Grid > This;

      typedef __PolygonGrid::EntitySeed< typename Item::Index, codim > EntitySeedImpl;
      typedef __PolygonGrid::Geometry< 2 - codim, 2, Grid > GeometryImpl;

      typedef typename std::remove_const< Grid >::type::ctype ctype;

    public:
      static const int codimension = codim;
      static const int dimension = 2;
      static const int mydimension = dimension - codimension;

      template< int cd >
      struct Codim
      {
        typedef Dune::Entity< cd, 2, Grid, __PolygonGrid::Entity > Entity;
      };

      typedef Dune::EntitySeed< Grid, EntitySeedImpl > EntitySeed;
      typedef Dune::Geometry< 2 - codim, 2, Grid, __PolygonGrid::Geometry > Geometry;

      explicit BasicEntity ( const Item &item ) : item_( item ) {}
      BasicEntity () noexcept = default;

      GeometryType type () const { return GeometryTypes::none( mydimension ); }

      PartitionType partitionType () const { return InteriorEntity; }

      Geometry geometry () const { return Geometry( GeometryImpl( item() ) ); }

      EntitySeed seed () const { return EntitySeedImpl( item().index() ); }

      int level () const noexcept { return 0; }

      bool equals ( const This &other ) const { return (item_ == other.item_); }

      template< int cd >
      typename Codim< cd >::Entity subEntity ( int i ) const
      {
        typedef __PolygonGrid::Entity< cd, 2, Grid > EntityImpl;
        return EntityImpl( __PolygonGrid::subEntity( item(), Dune::Codim< cd - codimension >(), i ) );
      }

      std::size_t index () const { return item().uniqueIndex(); }

      const Item &item () const { return item_; }

    protected:
      Item item_;
    };



    // Entity for Codimension 2
    // ------------------------

    template< int dim, class Grid >
    class Entity< 2, dim, Grid >
      : public BasicEntity< 2, Node< typename std::remove_const< Grid >::type::ctype >, Grid >
    {
      typedef Entity< 2, dim, Grid > This;
      typedef BasicEntity< 2, Node< typename std::remove_const< Grid >::type::ctype >, Grid > Base;

      typedef Node< typename std::remove_const< Grid >::type::ctype > Item;

    public:
      using Base::item;

      explicit Entity ( const Item &item ) : Base( item ) {}
      Entity () noexcept = default;

      std::size_t subEntities ( int codim ) const noexcept { return (codim == 2 ? 1u : 0u); }

      std::size_t subIndex ( int codim, std::size_t i ) const noexcept
      {
        assert( i < subEntities( codim ) );
        return __PolygonGrid::subEntity( item(), Dune::Codim< 0 >(), i ).uniqueIndex();
      }
    };



    // Entity for Codimension 1
    // ------------------------

    template< int dim, class Grid >
    class Entity< 1, dim, Grid >
      : public BasicEntity< 1, HalfEdge< typename std::remove_const< Grid >::type::ctype >, Grid >
    {
      typedef Entity<1, dim, Grid > This;
      typedef BasicEntity< 1, HalfEdge< typename std::remove_const< Grid >::type::ctype >, Grid > Base;

      typedef HalfEdge< typename std::remove_const< Grid >::type::ctype > Item;

    public:
      using Base::item;

      explicit Entity ( const Item &item ) : Base( item ) {}
      Entity () noexcept = default;

      std::size_t subEntities ( int codim ) const noexcept { return (codim == 2 ? 2u : (codim == 1 ? 1u : 0u)); }

      std::size_t subIndex ( int codim, std::size_t i ) const noexcept
      {
        assert( i < subEntities( codim ) );
        if( codim == 2 )
          return __PolygonGrid::subEntity( item(), Dune::Codim< 0 >(), i ).uniqueIndex();
        else
          return __PolygonGrid::subEntity( item(), Dune::Codim< 1 >(), i ).uniqueIndex();
      }
    };



    // Entity for codimension 0
    // ------------------------

    template< int dim, class Grid >
    class Entity< 0, dim, Grid >
      : public BasicEntity< 0, Node< typename std::remove_const< Grid >::type::ctype >, Grid >
    {
      typedef Entity< 0, dim, Grid > This;
      typedef BasicEntity< 0, Node< typename std::remove_const< Grid >::type::ctype >, Grid > Base;

      typedef Node< typename std::remove_const< Grid >::type::ctype > Item;

      typedef __PolygonGrid::EntityIterator< 0, Grid > HierarchicIteratorImpl;

    public:
      typedef typename Base::Geometry LocalGeometry;

      typedef Dune::EntityIterator< 0, Grid, HierarchicIteratorImpl > HierarchicIterator;

      using Base::item;

      explicit Entity ( const Item &item ) : Base( item ) {}
      Entity () noexcept = default;

      unsigned int subEntities ( int codim ) const noexcept
      {
        return ((codim == 1) || (codim == 2) ? item().halfEdges().size() : (codim == 0u ? 1u : 0u));
      }

      template< int codim >
      int count () const
      {
        return subEntities( codim );
      }

      std::size_t subIndex ( int codim, std::size_t i ) const noexcept
      {
        assert( i < subEntities( codim ) );
        switch( codim )
        {
        case 0:
          return __PolygonGrid::subEntity( item(), Dune::Codim< 0 >(), i ).uniqueIndex();

        case 1:
          return __PolygonGrid::subEntity( item(), Dune::Codim< 1 >(), i ).uniqueIndex();

        case 2:
          return __PolygonGrid::subEntity( item(), Dune::Codim< 2 >(), i ).uniqueIndex();

        default:
          std::terminate();
        }
      }

      bool isLeaf () const noexcept { return true; }

      Dune::Entity< 0, 2, Grid, __PolygonGrid::Entity > father () const { assert( hasFather() ); std::terminate(); }

      bool hasFather () const { return false; }

      LocalGeometry geometryInFather () const { assert( hasFather() ); std::terminate(); }

      HierarchicIterator hbegin ( int maxLevel ) const { return HierarchicIteratorImpl(); }
      HierarchicIterator hend ( int maxLevel ) const { return HierarchicIteratorImpl(); }

      bool isRegular () const { return true; }
      bool isNew () const { return false; }
      bool mightVanish () const { return false; }

      bool hasBoundaryIntersections () const
      {
        bool hasBoundaryIntersections = false;
        for( const auto halfEdge : item().halfEdges() )
          hasBoundaryIntersections |= !halfEdge.neighbor().regular();
        return hasBoundaryIntersections;
      }
    };

 } // namespace __PolygonGrid

} // namespace Dune

#endif // #ifndef DUNE_POLYGONGRID_ENTITY_HH
